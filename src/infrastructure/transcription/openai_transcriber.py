from openai import Client

from src.core.models import AudioData, TranscriptionResult
from src.infrastructure.transcription.base import Transcriber


class OpenAITranscriber(Transcriber):

    def __init__(self, api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = Client(api_key=api_key)

    async def transcribe(self, audio: AudioData) -> TranscriptionResult:
        """Transcribe audio to text"""
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=(f"audio.{audio.format}", audio.file, f"audio/{audio.format}"),
        )
        print(f"Transcribed text: {transcription.text}")
        return TranscriptionResult(text=transcription.text)
