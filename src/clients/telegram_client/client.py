import httpx

from src.core.context import get_request_id
from src.core.models import AudioData


class MemoAPIClient:
    def __init__(self, base_url: str, version: str = "v1"):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            follow_redirects=True,
            timeout=600,
        )
        self.version = version

    async def store_memo(self, audio: AudioData, user_id: str):
        files = {
            "audio": (f"audio.{audio.format}", audio.file, f"audio/{audio.format}")
        }
        response = await self.client.post(
            f"/{self.version}/memos",
            params={"user_id": user_id},
            files=files,
            headers={"X-Request-ID": get_request_id()},
        )
        return response.json()

    async def search_memos(self, query: str, user_id: str):
        response = await self.client.post(
            f"/{self.version}/search",
            json={"query": query, "user_id": user_id, "limit": 7},
            headers={"X-Request-ID": get_request_id()},
        )
        return response.json()

    async def delete_memo(self, user_id: str, memo_id: str):
        response = await self.client.delete(
            f"/{self.version}/memos/{memo_id}",
            params={"user_id": user_id},
        )
        return response.json()
