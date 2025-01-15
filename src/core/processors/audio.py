from src.core.models import AudioData, TranscriptionResult
from src.infrastructure.transcription.base import Transcriber


class AudioProcessor:
    def __init__(self, transcriber: Transcriber):
        self.transcriber = transcriber

    async def process(self, audio: AudioData) -> TranscriptionResult:
        """Process audio and return transcription"""
        return await self.transcriber.transcribe(audio)
