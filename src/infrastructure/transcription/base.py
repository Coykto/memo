from abc import ABC, abstractmethod

from src.core.models import AudioData, TranscriptionResult


class Transcriber(ABC):
    @abstractmethod
    async def transcribe(self, audio: AudioData) -> TranscriptionResult:
        """Transcribe audio to text"""
        pass
