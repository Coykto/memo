from src.core.models import VectorData
from src.infrastructure.vectorization.base import Vectorizer


class TextProcessor:
    def __init__(self, vectorizer: Vectorizer):
        self.vectorizer = vectorizer

    async def process(self, text: str) -> VectorData:
        """Process text and return vector representation"""
        return await self.vectorizer.vectorize(text)
