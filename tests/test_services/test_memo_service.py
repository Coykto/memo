import io
from unittest.mock import AsyncMock

import pytest
from anthropic import AnthropicError
from openai import OpenAIError

from src.core.models import AudioData, TranscriptionResult, VectorData, Summary, Memo
from src.core.services.memo import MemoService


async def test_create_memo_complete_flow():
    # Set up test data
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"
    test_transcription = "This is a test transcription"
    test_summary = "Test Summary Title"
    test_vector = [0.1, 0.2, 0.3]
    test_memo_id = "test-memo-123"

    # Configure mocks
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.return_value = TranscriptionResult(
        text=test_transcription
    )

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.return_value = Summary(
        text=test_transcription, summary=test_summary
    )

    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=test_transcription, metadata={}
    )

    mock_storage = AsyncMock()
    mock_storage.store_memo.return_value = test_memo_id
    mock_storage.get_memo.return_value = Memo(
        id=test_memo_id,
        text=test_transcription,
        title=test_summary,
        user_id=test_user_id,
        vector=test_vector,
    )

    mock_vector_storage = AsyncMock()

    # Create service instance
    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Execute the service method
    result = await service.create_memo_from_audio(test_audio, test_user_id)

    # Verify all mock calls happened in the expected order with correct parameters
    mock_audio_processor.process.assert_called_once_with(test_audio)
    mock_summarizer.summarize.assert_called_once_with(test_transcription)
    mock_text_processor.process.assert_called_once_with(test_transcription)
    mock_storage.store_memo.assert_called_once_with(
        text=test_transcription, title=test_summary, user_id=test_user_id
    )
    mock_vector_storage.store_vector.assert_called_once_with(
        test_vector, memo_id=test_memo_id, metadata={"user_id": test_user_id}
    )
    mock_storage.get_memo.assert_called_once_with(test_memo_id)

    # Verify the result
    assert result.id == test_memo_id
    assert result.text == test_transcription
    assert result.title == test_summary
    assert result.user_id == test_user_id
    assert result.vector == test_vector


async def test_create_memo_transcription_error():
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"

    # Configure audio processor to fail
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.side_effect = OpenAIError("Transcription failed")

    # Other mocks (shouldn't be called)
    mock_summarizer = AsyncMock()
    mock_text_processor = AsyncMock()
    mock_storage = AsyncMock()
    mock_vector_storage = AsyncMock()

    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Verify the error is propagated
    with pytest.raises(OpenAIError) as exc_info:
        await service.create_memo_from_audio(test_audio, test_user_id)

    assert "Transcription failed" in str(exc_info.value)

    # Verify no other operations were performed
    mock_summarizer.summarize.assert_not_called()
    mock_text_processor.process.assert_not_called()
    mock_storage.store_memo.assert_not_called()
    mock_vector_storage.store_vector.assert_not_called()


async def test_create_memo_summarization_error():
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"
    test_transcription = "This is a test transcription"

    # Configure mocks for the failure scenario
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.return_value = TranscriptionResult(
        text=test_transcription
    )

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.side_effect = AnthropicError("Summarization failed")

    mock_text_processor = AsyncMock()
    mock_storage = AsyncMock()
    mock_vector_storage = AsyncMock()

    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Verify the error is propagated
    with pytest.raises(AnthropicError) as exc_info:
        await service.create_memo_from_audio(test_audio, test_user_id)

    assert "Summarization failed" in str(exc_info.value)

    # Verify later operations were not performed
    mock_text_processor.process.assert_not_called()
    mock_storage.store_memo.assert_not_called()
    mock_vector_storage.store_vector.assert_not_called()


async def test_create_memo_vectorization_error():
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"
    test_transcription = "This is a test transcription"
    test_summary = "Test Summary Title"

    # Configure mocks for the failure scenario
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.return_value = TranscriptionResult(
        text=test_transcription
    )

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.return_value = Summary(
        text=test_transcription, summary=test_summary
    )

    mock_text_processor = AsyncMock()
    mock_text_processor.process.side_effect = OpenAIError("Vectorization failed")

    mock_storage = AsyncMock()
    mock_vector_storage = AsyncMock()

    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Verify the error is propagated
    with pytest.raises(OpenAIError) as exc_info:
        await service.create_memo_from_audio(test_audio, test_user_id)

    assert "Vectorization failed" in str(exc_info.value)

    # Verify storage operations were not performed
    mock_storage.store_memo.assert_not_called()
    mock_vector_storage.store_vector.assert_not_called()


async def test_create_memo_storage_error():
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"
    test_transcription = "This is a test transcription"
    test_summary = "Test Summary Title"
    test_vector = [0.1, 0.2, 0.3]

    # Configure mocks for the failure scenario
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.return_value = TranscriptionResult(
        text=test_transcription
    )

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.return_value = Summary(
        text=test_transcription, summary=test_summary
    )

    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=test_transcription, metadata={}
    )

    mock_storage = AsyncMock()
    mock_storage.store_memo.side_effect = Exception("Storage error")

    mock_vector_storage = AsyncMock()

    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Verify the error is propagated
    with pytest.raises(Exception) as exc_info:
        await service.create_memo_from_audio(test_audio, test_user_id)

    assert "Storage error" in str(exc_info.value)

    # Verify vector storage was not called
    mock_vector_storage.store_vector.assert_not_called()


async def test_create_memo_vector_storage_error():
    test_audio = AudioData(file=io.BytesIO(b"test audio content"), format="wav")
    test_user_id = "test-user-123"
    test_transcription = "This is a test transcription"
    test_summary = "Test Summary Title"
    test_vector = [0.1, 0.2, 0.3]
    test_memo_id = "test-memo-123"

    # Configure mocks for the failure scenario
    mock_audio_processor = AsyncMock()
    mock_audio_processor.process.return_value = TranscriptionResult(
        text=test_transcription
    )

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.return_value = Summary(
        text=test_transcription, summary=test_summary
    )

    mock_text_processor = AsyncMock()
    mock_text_processor.process.return_value = VectorData(
        vector=test_vector, text=test_transcription, metadata={}
    )

    mock_storage = AsyncMock()
    mock_storage.store_memo.return_value = test_memo_id

    mock_vector_storage = AsyncMock()
    mock_vector_storage.store_vector.side_effect = Exception("Vector storage error")

    service = MemoService(
        audio_processor=mock_audio_processor,
        text_processor=mock_text_processor,
        vector_storage=mock_vector_storage,
        storage=mock_storage,
        summarizer=mock_summarizer,
    )

    # Verify the error is propagated
    with pytest.raises(Exception) as exc_info:
        await service.create_memo_from_audio(test_audio, test_user_id)

    assert "Vector storage error" in str(exc_info.value)

    # Verify we tried to store in both places
    mock_storage.store_memo.assert_called_once()
    mock_vector_storage.store_vector.assert_called_once()
