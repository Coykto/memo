# import pytest
# from src.infrastructure.transcription.openai_transcriber import OpenAITranscriber
#
#
# @pytest.mark.asyncio
# async def test_openai_transcription():
#     with patch('openai.Client') as mock_client:
#         mock_client.return_value.audio.transcriptions.create.return_value = \
#             MagicMock(text="Test transcription")
#
#         transcriber = OpenAITranscriber(api_key="test-key")
#         audio_data = AudioData(
#             file=io.BytesIO(b"test audio content"),
#             format="wav"
#         )
#
#         result = await transcriber.transcribe(audio_data)
#         assert result.text == "Test transcription"
