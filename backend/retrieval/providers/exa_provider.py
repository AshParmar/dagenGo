from exa_py import Exa

from config import settings
from retrieval.providers.base_provider import BaseSearchProvider


class ExaProvider(BaseSearchProvider):

    def __init__(self):

        self.client = Exa(
            api_key=settings.EXA_API_KEY
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ):

        response = self.client.search_and_contents(
            query=query,
            num_results=top_k,
            text=True,
        )

        documents = []

        for result in response.results:

            documents.append(
                {
                    "title": result.title,
                    "url": result.url,
                    "text": result.text,
                }
            )

        return documents