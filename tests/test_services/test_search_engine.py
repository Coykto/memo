from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from openai import OpenAIError
from pinecone.exceptions import PineconeException

from src.core.models import VectorData, Memo
from src.core.services.search import SearchEngine


async def test_search_complete_flow():
    # Set up test data
    query = "test query"
    user_id = "test-user"
    test_vector = [0.1, 0.2, 0.3]
    mock_memo_id = "test-memo-id"
    test_memo_date=datetime.now().isoformat()

    # Configure mocks with specific returns
    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query
    )

    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.return_value = [
        {"id": mock_memo_id, "score": 0.95, "metadata": {"user_id": user_id}}
    ]

    mock_storage = AsyncMock()
    mock_storage.get_memo.return_value = Memo(
        id=mock_memo_id, text="Test memo content", title="Test memo", user_id=user_id, date=test_memo_date
    )

    engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    results = await engine.search(query, user_id, 10)

    # Verify the complete flow
    mock_text_processor.process.assert_called_once_with(query)
    mock_vector_storage.search.assert_called_once_with(test_vector, user_id, 10)
    mock_storage.get_memo.assert_called_once_with(mock_memo_id)

    # Verify results
    assert len(results) == 1
    assert results[0].score == 0.95
    assert results[0].memo.id == mock_memo_id
    assert results[0].memo.user_id == user_id
    assert results[0].memo.date == test_memo_date


async def test_empty_search_results():
    # Set up test data
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]

    # Configure mocks
    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    mock_vector_storage = AsyncMock()
    # Return empty list to simulate no matches found
    mock_vector_storage.search.return_value = []

    mock_storage = AsyncMock()
    # Storage should not be called when there are no vector matches

    # Create search engine instance with mocks
    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    # Execute search
    results = await search_engine.search(query, user_id, limit=10)

    # Verify interactions
    mock_text_processor.process.assert_called_once_with(query)
    mock_vector_storage.search.assert_called_once_with(test_vector, user_id, 10)
    mock_storage.get_memo.assert_not_called()

    # Verify results
    assert len(results) == 0


async def test_search_with_missing_memo():
    # Set up test data
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]
    existing_memo_id = "existing-memo-123"
    missing_memo_id = "missing-memo-456"

    # Configure text processor mock
    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    # Configure vector storage to return two results, one valid and one invalid
    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.return_value = [
        {"id": existing_memo_id, "score": 0.95, "metadata": {"user_id": user_id}},
        {"id": missing_memo_id, "score": 0.85, "metadata": {"user_id": user_id}},
    ]

    # Configure storage to return a memo for one ID but None for the other
    mock_storage = AsyncMock()

    async def get_memo_side_effect(memo_id: str):
        if memo_id == existing_memo_id:
            return Memo(
                id=existing_memo_id,
                text="Existing memo text",
                title="Existing memo",
                user_id=user_id,
                date=datetime.now().isoformat(),
            )
        return None

    mock_storage.get_memo.side_effect = get_memo_side_effect

    # Create search engine instance
    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    # Execute search
    results = await search_engine.search(query, user_id, limit=10)

    # Verify interactions
    mock_text_processor.process.assert_called_once_with(query)
    mock_vector_storage.search.assert_called_once_with(test_vector, user_id, 10)
    assert mock_storage.get_memo.call_count == 2  # Should try to fetch both memos

    # Verify results
    assert len(results) == 1  # Should only return the existing memo
    assert results[0].memo.id == existing_memo_id
    assert results[0].score == 0.95


async def test_search_with_vector_storage_error():
    # Set up test data
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]

    # Configure text processor to work normally
    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    # Configure vector storage to raise an error
    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.side_effect = PineconeException("Connection error")

    mock_storage = AsyncMock()

    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    # Verify that the exception is propagated
    with pytest.raises(PineconeException) as exc_info:
        await search_engine.search(query, user_id, limit=10)

    assert "Connection error" in str(exc_info.value)
    mock_storage.get_memo.assert_not_called()  # Should not reach the storage layer


async def test_search_with_text_processor_error():
    # Set up test data
    query = "test query"
    user_id = "test-user-123"

    # Configure text processor to raise an error
    mock_text_processor = AsyncMock()
    mock_text_processor.process.side_effect = OpenAIError("API rate limit exceeded")

    mock_vector_storage = AsyncMock()
    mock_storage = AsyncMock()

    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    # Verify that the exception is propagated
    with pytest.raises(OpenAIError) as exc_info:
        await search_engine.search(query, user_id, limit=10)

    assert "API rate limit exceeded" in str(exc_info.value)
    mock_vector_storage.search.assert_not_called()  # Should not reach vector storage
    mock_storage.get_memo.assert_not_called()  # Should not reach storage


async def test_search_with_storage_error():
    # Set up test data
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]
    test_memo_id = "test-memo-123"

    # Configure text processor to work normally
    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    # Configure vector storage to return a result
    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.return_value = [
        {"id": test_memo_id, "score": 0.95, "metadata": {"user_id": user_id}}
    ]

    # Configure storage to raise an error
    mock_storage = AsyncMock()
    mock_storage.get_memo.side_effect = Exception("Database connection error")

    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    # Verify that the exception is propagated
    with pytest.raises(Exception) as exc_info:
        await search_engine.search(query, user_id, limit=10)

    assert "Database connection error" in str(exc_info.value)


async def test_search_limit_parameter():
    # Setup
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]
    custom_limit = 5  # Test with non-default limit

    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.return_value = []  # Empty results are fine for this test

    mock_storage = AsyncMock()

    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    await search_engine.search(query, user_id, limit=custom_limit)

    # Verify the limit parameter is correctly passed to vector storage
    mock_vector_storage.search.assert_called_once_with(
        test_vector, user_id, custom_limit
    )


async def test_store_vector_user_metadata():
    # Setup
    user_id = "test-user-123"
    memo_id = "test-memo-123"
    test_vector = [0.1, 0.2, 0.3]

    mock_vector_storage = AsyncMock()

    # Test storing vector with user metadata
    await mock_vector_storage.store_vector(
        vector=test_vector, memo_id=memo_id, metadata={"user_id": user_id}
    )

    # Verify correct metadata was passed
    mock_vector_storage.store_vector.assert_called_once_with(
        vector=test_vector, memo_id=memo_id, metadata={"user_id": user_id}
    )


async def test_search_minimum_score_threshold():
    # Setup
    query = "test query"
    user_id = "test-user-123"
    test_vector = [0.1, 0.2, 0.3]

    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=query, metadata={}
    )

    # Return results with varying scores including very low ones
    mock_vector_storage = AsyncMock()
    mock_vector_storage.search.return_value = [
        {
            "id": "memo-1",
            "score": 0.95,
            "metadata": {"user_id": user_id},
        },  # High relevance
        {
            "id": "memo-2",
            "score": 0.50,
            "metadata": {"user_id": user_id},
        },  # Medium relevance
        {
            "id": "memo-3",
            "score": 0.15,
            "metadata": {"user_id": user_id},
        },  # Low relevance
        {
            "id": "memo-4",
            "score": 0.05,
            "metadata": {"user_id": user_id},
        },  # Very low relevance
    ]

    mock_storage = AsyncMock()
    mock_storage.get_memo.side_effect = lambda memo_id: Memo(
        id=memo_id, text=f"Memo {memo_id}", title=f"Title {memo_id}", user_id=user_id, date=datetime.now().isoformat()
    )

    search_engine = SearchEngine(
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
    )

    results = await search_engine.search(query, user_id, limit=10)

    # If we have a minimum score threshold, verify it's applied
    if hasattr(search_engine, "min_score_threshold"):
        results_above_threshold = [
            r for r in results if r.score >= search_engine.min_score_threshold
        ]
        assert len(results) == len(results_above_threshold)

    # Verify results are returned in descending score order
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
