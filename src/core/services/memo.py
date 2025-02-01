from src.core.models import AudioData, Memo
from src.core.processors.audio import AudioProcessor
from src.core.processors.text import TextProcessor
from src.infrastructure.db.base import Storage
from src.infrastructure.summarization.base import Summarizer
from src.infrastructure.vector_db.base import VectorStorage


class MemoService:
    """Service responsible for memo creation and management"""

    def __init__(
        self,
        audio_processor: AudioProcessor,
        text_processor: TextProcessor,
        vector_storage: VectorStorage,
        storage: Storage,
        summarizer: Summarizer,
    ):
        self.audio_processor = audio_processor
        self.text_processor = text_processor
        self.vector_storage = vector_storage
        self.storage = storage
        self.summarizer = summarizer

    async def create_memo_from_audio(self, audio: AudioData, user_id: str) -> Memo:
        """Create a new memo from audio input"""
        # Transcribe and summarize audio
        transcription = await self.audio_processor.process(audio)
        memo_summary = await self.summarizer.summarize(transcription.text)

        # Generate vector
        vector_data = await self.text_processor.process(transcription.text)

        # Store in both databases
        memo_id = await self.storage.store_memo(text=transcription.text, title=memo_summary.summary, user_id=user_id)
        await self.vector_storage.store_vector(vector_data.vector, memo_id=memo_id, metadata={"user_id": user_id})

        memo = await self.storage.get_memo(memo_id)
        return Memo(
            id=memo_id,
            text=memo.text,
            title=memo.title,
            user_id=user_id,
            vector=vector_data.vector,
            date=memo.date,
        )
