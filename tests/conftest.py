import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.core.models import AudioData, Memo, TranscriptionResult, VectorData
from src.infrastructure.db.base import Storage
from src.infrastructure.summarization.base import Summarizer
from src.infrastructure.transcription.base import Transcriber
from src.infrastructure.vector_db.base import VectorStorage
from src.infrastructure.vectorization.base import Vectorizer


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_transcriber():
    class MockTranscriber(Transcriber):
        async def transcribe(self, audio: AudioData) -> TranscriptionResult:
            return TranscriptionResult(text="Test transcription")

    return MockTranscriber()


@pytest.fixture
def mock_vectorizer():
    class MockVectorizer(Vectorizer):
        async def vectorize(self, text: str) -> VectorData:
            return VectorData(vector=[0.1, 0.2, 0.3], text=text, metadata={})

    return MockVectorizer()


@pytest.fixture
def mock_vector_storage():
    class MockVectorStorage(VectorStorage):
        async def store_vector(self, vector: list[float], memo_id: str, metadata: dict):
            pass

        async def search(
            self, query_vector: list[float], user_id: str, limit: int = 10
        ) -> list[dict]:
            return [
                {"id": "test-memo-id", "score": 0.95, "metadata": {"user_id": user_id}}
            ]

    return MockVectorStorage()


@pytest.fixture
def mock_storage():
    class MockStorage(Storage):
        async def store_memo(self, text: str, title: str, user_id: str) -> str:
            return "test-memo-id"

        async def get_memo(self, memo_id: str) -> Memo:
            return Memo(
                id=memo_id,
                text="Test memo text",
                title="Test memo title",
                user_id="test-user",
                vector=[0.1, 0.2, 0.3],
            )

    return MockStorage()


@pytest.fixture
def mock_summarizer():
    class MockSummarizer(Summarizer):
        async def summarize(self, text: str, length: int = 50) -> str:
            return "Test summary"

    return MockSummarizer()


@pytest.fixture(autouse=True, scope="function")
def cleanup(test_client):
    yield
    # Clear any overridden dependencies
    test_client.app.dependency_overrides = {}
