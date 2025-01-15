from abc import ABC, abstractmethod

from src.core.models import Memo


class Storage(ABC):
    @abstractmethod
    async def store_memo(self, text: str, title: str, user_id: str) -> str:
        """Store memo text and return memo ID"""
        pass

    @abstractmethod
    async def get_memo(self, memo_id: str) -> Memo:
        """Retrieve memo text by ID"""
        pass
