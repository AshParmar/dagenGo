from retrieval.providers.base_provider import BaseSearchProvider
from retrieval.providers.provider_manager import ProviderManager


class WebSearch:

    def __init__(
        self,
        provider: BaseSearchProvider | None = None,
    ):

        self.provider = provider or ProviderManager()

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:

        return self.provider.search(
            query=query,
            top_k=top_k,
        )