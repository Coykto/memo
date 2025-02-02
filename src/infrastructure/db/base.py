from abc import ABC, abstractmethod
from typing import Optional

from src.core.models import Memo


class Storage(ABC):
    @abstractmethod
    async def store_memo(self, text: str, title: str, user_id: str) -> str:
        """Store memo text and return memo ID"""
        pass

    @abstractmethod
    async def get_memo(self, user_id: str, memo_id: str) -> Optional[Memo]:
        """Retrieve memo by ID"""
        pass

    @abstractmethod
    async def delete_memo(self, user_id: str, memo_id: str) -> Optional[Memo]:
        """Delete memo by ID"""
        pass
