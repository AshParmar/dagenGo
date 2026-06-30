from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self):
        self.documents = []
        self.tokenized_documents = []
        self.bm25 = None

    def index(self, documents: list[dict]):
        """Index documents for sparse retrieval."""
        self.documents = [document for document in documents if document.get("text")]

        self.tokenized_documents = [
            document["text"].split()
            for document in self.documents
        ]

        if not self.tokenized_documents:
            self.bm25 = None
            return

        self.bm25 = BM25Okapi(self.tokenized_documents)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:

        if self.bm25 is None:
            return []

        tokenized_query = query.split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results: list[dict] = []

        for document, score in ranked[:top_k]:
            enriched = dict(document)
            enriched["score"] = float(score)
            results.append(enriched)

        return results