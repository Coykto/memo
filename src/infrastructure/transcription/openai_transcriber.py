import logging

from openai import Client
from openai._exceptions import RateLimitError
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from src.core.models import AudioData, TranscriptionResult
from src.infrastructure.transcription.base import Transcriber


class OpenAITranscriber(Transcriber):

    def __init__(self, api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = Client(api_key=api_key)

    @retry(
        wait=wait_exponential(min=3, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING),
    )
    async def transcribe(self, audio: AudioData) -> TranscriptionResult:
        """Transcribe audio to text"""
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=(f"audio.{audio.format}", audio.file, f"audio/{audio.format}"),
        )
        logging.info(f"Transcribed text: {transcription.text}")
        return TranscriptionResult(text=transcription.text)
