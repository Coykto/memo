from unittest.mock import AsyncMock

import pytest

from src.api.dependencies import get_search_engine
from src.core.models import Memo, SearchResult


@pytest.fixture
def mock_search_engine():
    return AsyncMock()


def test_search_memos_success(test_client, mock_search_engine):
    # Setup test data
    test_user_id = "test-user-123"
    test_query = "test query"
    test_memo = Memo(
        id="test-memo-id", text="Test content", title="Test title", user_id=test_user_id
    )

    # Configure mock to return results
    mock_search_engine.search.return_value = [SearchResult(memo=test_memo, score=0.95)]

    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Make request
    response = test_client.post(
        "/search/", json={"query": test_query, "user_id": test_user_id, "limit": 10}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert len(data["results"]) == 1
    assert data["total"] == 1

    # Verify service interaction
    mock_search_engine.search.assert_called_once_with(test_query, test_user_id, 10)


def test_search_memos_empty_results(test_client, mock_search_engine):
    # Configure mock to return empty results
    mock_search_engine.search.return_value = []

    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Make request
    response = test_client.post(
        "/search/",
        json={"query": "no results query", "user_id": "test-user", "limit": 10},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["total"] == 0


def test_search_memos_missing_required_fields(test_client, mock_search_engine):
    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Test missing query
    response = test_client.post("/search/", json={"user_id": "test-user"})
    assert response.status_code == 422

    # Test missing user_id
    response = test_client.post("/search/", json={"query": "test query"})
    assert response.status_code == 422


def test_search_memos_invalid_limit(test_client, mock_search_engine):
    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Test negative limit
    response = test_client.post(
        "/search/", json={"query": "test query", "user_id": "test-user", "limit": -1}
    )
    assert response.status_code == 422

    # Test zero limit
    response = test_client.post(
        "/search/", json={"query": "test query", "user_id": "test-user", "limit": 0}
    )
    assert response.status_code == 422


def test_search_memos_invalid_json(test_client, mock_search_engine):
    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Send invalid JSON
    response = test_client.post("/search/", data="not a json")
    assert response.status_code == 422


def test_search_memos_service_error(test_client, mock_search_engine):
    # Configure mock to raise an error
    mock_search_engine.search.side_effect = Exception("Search service error")

    # Override dependency
    test_client.app.dependency_overrides[get_search_engine] = lambda: mock_search_engine

    # Make request
    response = test_client.post(
        "/search/", json={"query": "test query", "user_id": "test-user", "limit": 10}
    )

    # Verify response
    assert response.status_code == 500
    data = response.json()
    assert "message" in data
    assert "error" in data["message"].lower()
