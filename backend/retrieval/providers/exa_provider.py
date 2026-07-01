from typing import Any

from config import settings
from retrieval.providers.base_provider import BaseSearchProvider


class ExaProvider(BaseSearchProvider):

    def __init__(self):

        if not settings.EXA_API_KEY:
            raise RuntimeError("EXA_API_KEY is not set — skipping Exa provider.")

        try:
            exa_module = __import__("exa_py", fromlist=["Exa"])
        except ImportError as exc:
            raise RuntimeError(
                "exa_py is required for ExaProvider. Install the backend dependencies to enable Exa search."
            ) from exc

        self.client: Any = exa_module.Exa(
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