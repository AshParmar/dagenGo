from retrieval.providers.base_provider import BaseSearchProvider


class WebSearch:

    def __init__(
        self,
        provider: BaseSearchProvider,
    ):

        self.provider = provider

    def search(
        self,
        query: str,
        top_k: int = 10,
    ):

        return self.provider.search(
            query=query,
            top_k=top_k,
        )