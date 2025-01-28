import logging

from openai import Client
from openai._exceptions import RateLimitError
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
)

from src.core.models import VectorData
from src.infrastructure.vectorization.base import Vectorizer


class OpenAIVectorizer(Vectorizer):
    def __init__(self, api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = Client(api_key=api_key)

    @retry(
        wait=wait_exponential(min=3, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING),
    )
    async def vectorize(self, text: str) -> VectorData:
        """Convert text to vector representation"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002", input=text, encoding_format="float"
        )
        return VectorData(vector=response.data[0].embedding, text=text, metadata={})
