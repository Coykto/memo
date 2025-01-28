from pinecone import Pinecone

from src.infrastructure.vector_db.base import VectorStorage


class PineconeVectorStorage(VectorStorage):
    def __init__(self, api_key: str, host: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(host=host)

    async def store_vector(self, vector: list[float], memo_id: str, metadata: dict):
        """Store vector in database"""
        self.index.upsert(
            vectors=[{"id": memo_id, "values": vector, "metadata": metadata}]
        )

    async def search(
        self, query_vector: list[float], user_id: str, limit: int = 3
    ) -> list[dict]:
        """Search for similar vectors"""
        response = self.index.query(
            vector=query_vector,
            top_k=limit,
            # include_values=True,
            include_metadata=True,
            filter={"user_id": {"$eq": user_id}},
        )

        return [
            {"id": match.id, "score": match.score, "metadata": match.metadata}
            for match in response.matches
        ]
