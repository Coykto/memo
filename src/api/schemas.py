# src/api/schemas.py
from typing import List

from pydantic import BaseModel

from src.core.models import Memo, SearchResult


class MemoCreate(BaseModel):
    """Request schema for creating a memo"""

    text: str
    title: str
    user_id: str


class MemoResponse(BaseModel):
    """Response schema for memo operations"""

    id: str
    text: str
    title: str

    @classmethod
    def from_memo(cls, memo: Memo) -> "MemoResponse":
        return cls(id=memo.id, text=memo.text, title=memo.title)


class SearchQuery(BaseModel):
    """Request schema for search"""

    query: str
    user_id: str
    limit: int = 10


class SearchResponse(BaseModel):
    """Response schema for search results"""

    results: List[MemoResponse]
    total: int

    @classmethod
    def from_search_results(cls, results: List[SearchResult]) -> "SearchResponse":
        return cls(
            results=[MemoResponse.from_memo(r.memo) for r in results],
            total=len(results),
        )
