import io
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.api.dependencies import get_memo_service
from src.core.models import Memo


@pytest.fixture
def mock_memo_service():
    return AsyncMock()


def test_create_memo_success(test_client, mock_memo_service):
    # Setup test data
    test_user_id = "test-user-123"
    test_memo = Memo(
        id="test-memo-id",
        text="Test transcription",
        title="Test title",
        user_id=test_user_id,
        date=datetime.now().isoformat(),
    )

    # Configure mock service to return our test memo
    mock_memo_service.create_memo_from_audio.return_value = test_memo

    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Create test file
    test_file = io.BytesIO(b"test audio content")
    test_file.name = "test.wav"

    # Make request
    response = test_client.post(
        f"/v1/memos/?user_id={test_user_id}",
        files={"audio": ("test.wav", test_file, "audio/wav")},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_memo.id
    assert data["text"] == test_memo.text
    assert data["title"] == test_memo.title

    # Verify service was called with correct parameters
    mock_memo_service.create_memo_from_audio.assert_called_once()
    call_args = mock_memo_service.create_memo_from_audio.call_args
    audio_data = call_args[0][0]
    assert hasattr(audio_data.file, "read"), "File object should be readable"
    assert audio_data.format == "wav"
    assert call_args[0][1] == test_user_id


def test_create_memo_missing_user_id(test_client, mock_memo_service):
    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Create test file
    test_file = io.BytesIO(b"test audio content")

    # Make request without user_id
    response = test_client.post(
        "/v1/memos/", files={"audio": ("test.wav", test_file, "audio/wav")}
    )

    # Verify response
    assert response.status_code == 422  # Validation error
    mock_memo_service.create_memo_from_audio.assert_not_called()


def test_create_memo_missing_file(test_client, mock_memo_service):
    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Make request without file
    response = test_client.post("/v1/memos/?user_id=test-user")

    # Verify response
    assert response.status_code == 422  # Validation error
    mock_memo_service.create_memo_from_audio.assert_not_called()


def test_create_memo_invalid_file_type(test_client, mock_memo_service):
    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Create test file with invalid type
    test_file = io.BytesIO(b"test content")

    # Make request with text file instead of audio
    response = test_client.post(
        "/v1/memos/?user_id=test-user",
        files={"audio": ("test.txt", test_file, "text/plain")},
    )

    # Verify response
    assert response.status_code == 400  # Bad request
    mock_memo_service.create_memo_from_audio.assert_not_called()


def test_create_memo_service_error(test_client, mock_memo_service):
    # Setup test data
    test_user_id = "test-user-123"

    # Configure mock to raise an exception
    mock_memo_service.create_memo_from_audio.side_effect = Exception("Service error")

    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Create test file
    test_file = io.BytesIO(b"test audio content")

    # Make request
    response = test_client.post(
        f"/v1/memos/?user_id={test_user_id}",
        files={"audio": ("test.wav", test_file, "audio/wav")},
    )

    # Verify response
    assert response.status_code == 500
    assert {
        "detail": "An unexpected error occurred",
        "message": "Internal server error",
    } == response.json()


def test_create_memo_empty_file(test_client, mock_memo_service):
    empty_file = io.BytesIO(b"")

    response = test_client.post(
        "/v1/memos/?user_id=test-user",
        files={"audio": ("empty.wav", empty_file, "audio/wav")},
    )

    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]


@pytest.mark.parametrize(
    "filename, file_obj, service_called",
    [
        ("empty.wav", io.BytesIO(b""), True),
        ("corrupt.wav", io.BytesIO(b"This is not valid audio data"), True),
        ("truncated.wav", io.BytesIO(b"RIFF1234WAVEfmt "), True),
        ("no_ext", io.BytesIO(b"test"), False),
        ("wrong.txt", io.BytesIO(b"wrong format"), False),
    ],
    ids=[
        "Empty file",
        "Corrupted content",
        "Truncated WAV header",
        "Missing extension",
        "Wrong format",
    ],
)
def test_create_memo_malformed_audio(
    test_client, mock_memo_service, filename, file_obj, service_called
):
    """Test handling of malformed audio files"""
    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    response = test_client.post(
        "/v1/memos/?user_id=test-user",
        files={"audio": (filename, file_obj, "audio/wav")},
    )

    # Verify response
    assert response.status_code == 400

    if not service_called:
        # Verify service was not called
        mock_memo_service.create_memo_from_audio.assert_not_called()

        # Reset mock for next iteration
        mock_memo_service.create_memo_from_audio.reset_mock()


# ==
def test_delete_memo_success(test_client, mock_memo_service):
    # Setup test data
    test_user_id = "test-user-123"
    test_memo_id = "test-memo-123"
    test_memo = Memo(
        id=test_memo_id,
        text="Test memo content",
        title="Test memo title",
        user_id=test_user_id,
        date=datetime.now().isoformat(),
    )

    # Configure mock service to return our test memo
    mock_memo_service.delete_memo.return_value = test_memo

    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Make request
    response = test_client.delete(f"/v1/memos/{test_memo_id}?user_id={test_user_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_memo_id
    assert data["text"] == test_memo.text
    assert data["title"] == test_memo.title

    # Verify service was called with correct parameters
    mock_memo_service.delete_memo.assert_called_once_with(test_user_id, test_memo_id)


def test_delete_memo_not_found(test_client, mock_memo_service):
    # Configure mock service to return None (memo not found)
    mock_memo_service.delete_memo.return_value = None

    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Make request
    response = test_client.delete("/v1/memos/nonexistent-memo?user_id=test-user")

    # Verify response
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["details"].lower()


def test_delete_memo_missing_user_id(test_client, mock_memo_service):
    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Make request without user_id
    response = test_client.delete("/v1/memos/test-memo-123")

    # Verify response
    assert response.status_code == 422
    mock_memo_service.delete_memo.assert_not_called()


def test_delete_memo_service_error(test_client, mock_memo_service):
    # Configure mock to raise an exception
    mock_memo_service.delete_memo.side_effect = Exception("Service error")

    # Override dependency
    test_client.app.dependency_overrides[get_memo_service] = lambda: mock_memo_service

    # Make request
    response = test_client.delete("/v1/memos/test-memo-123?user_id=test-user")

    # Verify response
    assert response.status_code == 500
    assert "Internal server error" in response.json()["message"]
