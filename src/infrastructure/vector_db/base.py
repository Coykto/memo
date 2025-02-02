from abc import ABC, abstractmethod


class VectorStorage(ABC):
    @abstractmethod
    async def store_vector(self, vector: list[float], memo_id: str, metadata: dict):
        """Store vector in database"""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    async def delete_vector(self, memo_id: str):
        """Delete vector from database"""
        pass
