# import pytest
# from fastapi.testclient import TestClient
#
#
# def test_search_memos(test_client):
#     response = test_client.post(
#         "/search/",
#         json={
#             "query": "test query",
#             "user_id": "test-user",
#             "limit": 10
#         }
#     )
#
#     assert response.status_code == 200
#     data = response.json()
#     assert "results" in data
#     assert "total" in data
#     assert len(data["results"]) > 0
#
#
# def test_search_memos_invalid_request(test_client):
#     response = test_client.post(
#         "/search/",
#         json={
#             "invalid": "data"
#         }
#     )
#     assert response.status_code == 422
