from fastapi import APIRouter, Depends
from starlette import status

from src.api.dependencies import get_search_engine
from src.api.schemas import SearchQuery, SearchResponse
from src.core.services.search import SearchEngine

router = APIRouter(prefix="/v1/search")


@router.post(
    "/",
    response_model=SearchResponse,
    summary="Search Voice Memos",
    description="""
    Search through voice memos using semantic search.
    
    The search endpoint uses vector similarity to find relevant voice memos based on the query text.
    Results are returned in order of relevance, with a similarity score for each result.""",
    status_code=status.HTTP_200_OK,
)
async def search_memos(
    query: SearchQuery, search_engine: SearchEngine = Depends(get_search_engine)
):
    results = await search_engine.search(query.query, query.user_id, query.limit)
    return SearchResponse.from_search_results(results)
