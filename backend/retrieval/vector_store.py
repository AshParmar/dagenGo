from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
)

from config import settings


class VectorStore:

    def __init__(self):

        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

        self.collection_name = settings.COLLECTION_NAME

    def create_collection(self):

        collections = [
            collection.name
            for collection in self.client.get_collections().collections
        ]

        if self.collection_name not in collections:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,
                    distance=Distance.COSINE,
                ),
            )

    def add_documents(self, points: list[PointStruct]):

        self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points,
        )

    def similarity_search(
        self,
        query_vector: list[float],
        limit: int = 10,
    ):

        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )