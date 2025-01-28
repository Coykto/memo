import httpx

from core.context import get_request_id
from core.models import AudioData


class MemoAPIClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            follow_redirects=True,
            timeout=600,
        )

    async def store_memo(self, audio: AudioData, user_id: str):
        files = {
            "audio": (f"audio.{audio.format}", audio.file, f"audio/{audio.format}")
        }
        response = await self.client.post(
            "/memos",
            params={"user_id": user_id},
            files=files,
            headers={"X-Request-ID": get_request_id()},
        )
        return response.json()

    async def search_memos(self, query: str, user_id: str):
        response = await self.client.post(
            "/search",
            json={"query": query, "user_id": user_id},
            headers={"X-Request-ID": get_request_id()},
        )
        return response.json()
