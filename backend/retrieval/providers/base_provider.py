from abc import ABC, abstractmethod


class BaseSearchProvider(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int,
    ):
        pass