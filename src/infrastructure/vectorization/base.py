from abc import ABC, abstractmethod

from src.core.models import VectorData


class Vectorizer(ABC):
    @abstractmethod
    async def vectorize(self, text: str) -> VectorData:
        """Convert text to vector representation"""
        pass
