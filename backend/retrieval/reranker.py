from sentence_transformers import CrossEncoder

from graph.state import DagenGoState

from config import settings


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            settings.RERANKER_MODEL
        )

    def rerank(
        self,
        state: DagenGoState,
        top_k: int = 5,
    ) -> DagenGoState:

        query = state["rewritten_query"]

        documents = state["merged_results"]

        pairs = [
            (
                query,
                document["text"],
            )
            for document in documents
        ]

        scores = self.model.predict(
            pairs
        )

        reranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        state["reranked_results"] = [
            document
            for document, _ in reranked[:top_k]
        ]

        return state