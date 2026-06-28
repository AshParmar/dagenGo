from tavily import TavilyClient

from config import settings
from retrieval.providers.base_provider import BaseSearchProvider


class TavilyProvider(BaseSearchProvider):

    def __init__(self):

        self.client = TavilyClient(
            api_key=settings.TAVILY_API_KEY
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ):

        response = self.client.search(
            query=query,
            max_results=top_k,
            include_answer=False,
            include_raw_content=True,
        )

        documents = []

        for result in response["results"]:

            documents.append(
                {
                    "title": result["title"],
                    "url": result["url"],
                    "text": result["raw_content"]
                    or result["content"],
                }
            )

        return documents