# import pytest
# from fastapi.testclient import TestClient
#
#
# def test_create_memo(test_client):
#     with open("tests/fixtures/test_audio.wav", "rb") as f:
#         response = test_client.post(
#             "/memos/?user_id=test-user",
#             files={"audio": ("test_audio.wav", f, "audio/wav")}
#         )
#
#     assert response.status_code == 200
#     data = response.json()
#     assert "id" in data
#     assert "text" in data
#     assert "title" in data
#
#
# def test_create_memo_invalid_file(test_client):
#     response = test_client.post(
#         "/memos/?user_id=test-user",
#         files={"audio": ("test.txt", b"invalid audio", "text/plain")}
#     )
#     assert response.status_code == 400
