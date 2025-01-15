from openai import Client

from src.core.models import VectorData
from src.infrastructure.vectorization.base import Vectorizer


class OpenAIVectorizer(Vectorizer):
    def __init__(self, api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = Client(api_key=api_key)

    async def vectorize(self, text: str) -> VectorData:
        """Convert text to vector representation"""
        response = self.client.embeddings.create(model="text-embedding-ada-002", input=text, encoding_format="float")
        return VectorData(vector=response.data[0].embedding, text=text, metadata={})
