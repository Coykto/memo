import logging

from src.core.models import SearchResult
from src.core.processors.text import TextProcessor
from src.infrastructure.db.base import Storage
from src.infrastructure.vector_db.base import VectorStorage


class SearchEngine:
    def __init__(
        self,
        text_processor: TextProcessor,
        vector_storage: VectorStorage,
        storage: Storage,
    ):
        self.text_processor = text_processor
        self.vector_storage = vector_storage
        self.storage = storage

    async def search(self, query: str, user_id: str, limit: int) -> list[SearchResult]:

        # Convert text to vector
        vector_data = await self.text_processor.process(query)

        # Search vector database
        vector_results = await self.vector_storage.search(
            vector_data.vector, user_id, limit
        )

        # Fetch full texts from database
        results = []
        for vec_result in vector_results:
            memo = await self.storage.get_memo(user_id, vec_result["id"])
            if memo is None:
                logging.warning(
                    f"Memo {vec_result['id']} found in vector storage but missing from main storage",
                    extra={"user_id": user_id},
                )
                continue

            results.append(
                SearchResult(
                    memo=memo,
                    score=vec_result["score"],
                    metadata=vec_result["metadata"],
                )
            )

        return results
