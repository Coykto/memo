from abc import ABC, abstractmethod

from src.core.models import Summary


class Summarizer(ABC):

    @abstractmethod
    async def summarize(self, text: str, length: int = 50) -> Summary:
        pass
