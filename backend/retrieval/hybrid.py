from graph.state import DagenGoState

from retrieval.embeddings import embeddings
from retrieval.vector_store import VectorStore
from retrieval.bm25 import BM25Retriever


class HybridRetriever:

    def __init__(self):

        self.vector_store = VectorStore()
        self.bm25 = BM25Retriever()

    def dense_retrieval(
        self,
        query: str,
        top_k: int,
    ):

        query_embedding = embeddings.embed_query(query)

        return self.vector_store.similarity_search(
            query_vector=query_embedding,
            limit=top_k,
        )

    def sparse_retrieval(
        self,
        query: str,
        top_k: int,
    ):

        return self.bm25.retrieve(
            query=query,
            top_k=top_k,
        )

    def retrieve(
        self,
        state: DagenGoState,
        top_k: int = 10,
    ) -> DagenGoState:

        query = state["rewritten_query"]

        dense_results = self.dense_retrieval(
            query=query,
            top_k=top_k,
        )

        sparse_results = self.sparse_retrieval(
            query=query,
            top_k=top_k,
        )

        state["dense_results"] = dense_results
        state["sparse_results"] = sparse_results

        return state