from graph.state import DagenGoState


class RetrievalMerger:
    """
    Merge retrieval results using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, k: int = 60):
        self.k = k

    def _rrf_score(self, rank: int) -> float:
        return 1 / (self.k + rank)

    def merge(self, state: DagenGoState) -> DagenGoState:

        scores = {}

        retrieval_sets = [
            state.get("dense_results", []),
            state.get("sparse_results", []),
            state.get("graph_results", []),   # Later
        ]

        for results in retrieval_sets:

            for rank, document in enumerate(results, start=1):

                doc_id = document["id"]

                if doc_id not in scores:
                    scores[doc_id] = {
                        "document": document,
                        "score": 0.0,
                    }

                scores[doc_id]["score"] += self._rrf_score(rank)

        merged_results = sorted(
            scores.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        state["merged_results"] = [
            item["document"]
            for item in merged_results
        ]

        return state