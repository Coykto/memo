from fastapi import APIRouter, Depends

from src.api.dependencies import get_search_engine
from src.api.schemas import SearchQuery, SearchResponse
from src.core.services.search import SearchEngine

router = APIRouter(prefix="/search")


@router.post("/", response_model=SearchResponse)
async def search_memos(query: SearchQuery, search_engine: SearchEngine = Depends(get_search_engine)):
    results = await search_engine.search(query.query, query.user_id, query.limit)
    return SearchResponse.from_search_results(results)
