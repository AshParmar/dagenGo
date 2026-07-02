"""
Hybrid Retriever — Optimized with:
  1. Parallel dense + sparse retrieval using ThreadPoolExecutor
  2. Search result caching (TTL-based, keyed on query hash)
  3. Graceful degradation when Qdrant is unavailable
  4. Config-driven top_k and rerank_top_k

Expected latency improvement: sequential → parallel cuts retrieval time in half.
"""
import hashlib
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from config import settings
from graph.state import DagenGoState
from retrieval.bm25 import BM25Retriever
from retrieval.embeddings import embeddings
from retrieval.merge import RetrievalMerger
from retrieval.reranker import Reranker
from retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple TTL cache for dense retrieval results
# ---------------------------------------------------------------------------
_dense_cache: dict[str, tuple[list, float]] = {}
_dense_cache_lock = threading.Lock()


def _query_hash(query: str, top_k: int) -> str:
    return hashlib.md5(f"{query}|{top_k}".encode()).hexdigest()


def _cached_dense(key: str) -> list | None:
    with _dense_cache_lock:
        entry = _dense_cache.get(key)
        if entry is None:
            return None
        results, ts = entry
        if time.time() - ts > settings.EMBED_CACHE_TTL:
            del _dense_cache[key]
            return None
        return results


def _store_dense(key: str, results: list) -> None:
    with _dense_cache_lock:
        _dense_cache[key] = (results, time.time())


class HybridRetriever:
    """Hybrid retrieval: dense (Qdrant) + sparse (BM25) + RRF merge + cross-encoder rerank."""

    def __init__(self) -> None:
        try:
            self.vector_store: VectorStore | None = VectorStore()
        except Exception:
            self.vector_store = None
        self.bm25 = BM25Retriever()
        self.merger = RetrievalMerger()
        self.reranker = Reranker()
        self._collection_ready = False

    def _normalize_dense_results(self, results: list[Any]) -> list[dict]:
        normalized: list[dict] = []
        for item in results:
            payload = getattr(item, "payload", None) or {}
            doc_id = payload.get("id") or str(getattr(item, "id", ""))
            text = payload.get("text", "")
            if not doc_id or not text:
                continue
            normalized.append(
                {
                    "id": doc_id,
                    "text": text,
                    "title": payload.get("title", ""),
                    "url": payload.get("url", ""),
                    "score": float(getattr(item, "score", 0.0)),
                }
            )
        return normalized

    def dense_retrieval(self, query: str, top_k: int) -> list[dict]:
        """Run dense retrieval over Qdrant with caching."""
        if self.vector_store is None:
            return []

        cache_key = _query_hash(query, top_k)
        cached = _cached_dense(cache_key)
        if cached is not None:
            logger.debug("Dense retrieval cache hit for query='%s'", query[:50])
            return cached

        try:
            if not self._collection_ready:
                self.vector_store.create_collection()
                self._collection_ready = True

            query_embedding = embeddings.embed_query(query)
            results = self.vector_store.similarity_search(
                query_vector=query_embedding,
                limit=top_k,
            )
            normalized = self._normalize_dense_results(results)
            _store_dense(cache_key, normalized)
            return normalized
        except Exception as exc:
            logger.warning("Dense retrieval failed: %s", exc)
            return []

    def sparse_retrieval(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
        """Run BM25 retrieval over chunked evidence."""
        if not chunks:
            return []
        self.bm25.index(chunks)
        return self.bm25.retrieve(query=query, top_k=top_k)

    def retrieve(self, state: DagenGoState, top_k: int = 10) -> DagenGoState:
        """Run parallel hybrid retrieval and update graph state."""
        query = state.get("rewritten_query") or state.get("query", "")
        chunks = state.get("chunks", [])

        run_settings = state.get("settings") or {}
        top_k = int(run_settings.get("topK", top_k))
        hybrid_enabled = run_settings.get("hybridRetrieval", True)

        dense_results: list[dict] = []
        sparse_results: list[dict] = []

        if hybrid_enabled:
            # Run dense and sparse retrieval concurrently
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(self.dense_retrieval, query, top_k): "dense",
                    executor.submit(self.sparse_retrieval, query, chunks, top_k): "sparse",
                }
                for future in as_completed(futures):
                    label = futures[future]
                    try:
                        result = future.result()
                        if label == "dense":
                            dense_results = result
                        else:
                            sparse_results = result
                    except Exception as exc:
                        logger.warning("%s retrieval failed: %s", label, exc)
        else:
            sparse_results = self.sparse_retrieval(query=query, chunks=chunks, top_k=top_k)

        state["dense_results"] = dense_results
        state["sparse_results"] = sparse_results

        state = self.merger.merge(state)
        state = self.reranker.rerank(state)

        return state
