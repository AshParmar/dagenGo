import logging

from retrieval.providers.exa_provider import ExaProvider
from retrieval.providers.tavily_provider import TavilyProvider


logger = logging.getLogger(__name__)


class ProviderManager:

    def __init__(self):

        candidates = [ExaProvider, TavilyProvider]
        self.providers = []
        for Provider in candidates:
            try:
                self.providers.append(Provider())
            except Exception as exc:
                logger.info("Skipping %s: %s", Provider.__name__, exc)

    def search(
        self,
        query: str,
        top_k: int = 10,
    ):

        documents = []
        seen_urls = set()

        for provider in self.providers:

            try:

                results = provider.search(
                    query=query,
                    top_k=top_k,
                )

                for document in results:

                    if document["url"] in seen_urls:
                        continue

                    seen_urls.add(
                        document["url"]
                    )

                    documents.append(
                        document
                    )

            except Exception as e:
                logger.warning(
                    "%s search failed: %s",
                    provider.__class__.__name__,
                    e,
                )

        return documents