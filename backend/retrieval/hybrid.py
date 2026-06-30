import logging
from typing import Any

from graph.state import DagenGoState
from retrieval.bm25 import BM25Retriever
from retrieval.embeddings import embeddings
from retrieval.merge import RetrievalMerger
from retrieval.reranker import Reranker
from retrieval.vector_store import VectorStore


logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retrieval service: dense + sparse + merge + rerank."""

    def __init__(self) -> None:
        self.vector_store = VectorStore()
        self.bm25 = BM25Retriever()
        self.merger = RetrievalMerger()
        self.reranker = Reranker()
        self._collection_checked = False

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
        """Run dense retrieval over Qdrant."""
        try:
            if not self._collection_checked:
                self.vector_store.create_collection()
                self._collection_checked = True

            query_embedding = embeddings.embed_query(query)
            results = self.vector_store.similarity_search(
                query_vector=query_embedding,
                limit=top_k,
            )
            return self._normalize_dense_results(results)
        except Exception as exc:
            logger.warning("Dense retrieval failed: %s", exc)
            return []

    def sparse_retrieval(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
        """Run BM25 retrieval over chunked evidence."""
        self.bm25.index(chunks)
        return self.bm25.retrieve(query=query, top_k=top_k)

    def retrieve(self, state: DagenGoState, top_k: int = 10) -> DagenGoState:
        """Run complete hybrid retrieval and update graph state."""
        query = state.get("rewritten_query") or state.get("query", "")
        chunks = state.get("chunks", [])

        dense_results = self.dense_retrieval(query=query, top_k=top_k)
        sparse_results = self.sparse_retrieval(query=query, chunks=chunks, top_k=top_k)

        state["dense_results"] = dense_results
        state["sparse_results"] = sparse_results

        state = self.merger.merge(state)
        state = self.reranker.rerank(state)

        return state
