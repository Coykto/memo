from functools import lru_cache

from fastapi import Depends

from src.config.settings import Settings
from src.core.processors.audio import AudioProcessor
from src.core.processors.text import TextProcessor
from src.core.services.memo import MemoService
from src.core.services.search import SearchEngine
from src.infrastructure.db.base import Storage
from src.infrastructure.db.local_storage import LocalStorage
from src.infrastructure.summarization.base import Summarizer
from src.infrastructure.summarization.claude_summarizer import ClaudeSummarizer
from src.infrastructure.transcription.base import Transcriber
from src.infrastructure.transcription.openai_transcriber import OpenAITranscriber
from src.infrastructure.vector_db.base import VectorStorage
from src.infrastructure.vector_db.pinecone_vector_storage import PineconeVectorStorage
from src.infrastructure.vectorization.base import Vectorizer
from src.infrastructure.vectorization.open_ai_vectorizer import OpenAIVectorizer


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_vector_storage(
    settings: Settings = Depends(get_settings),
) -> PineconeVectorStorage:
    return PineconeVectorStorage(api_key=settings.pinecone_api_key, host=settings.pinecone_host)


def get_transcriber(settings: Settings = Depends(get_settings)) -> OpenAITranscriber:
    return OpenAITranscriber(api_key=settings.openai_api_key)


def get_vectorizer(settings: Settings = Depends(get_settings)) -> OpenAIVectorizer:
    return OpenAIVectorizer(api_key=settings.openai_api_key)


def get_summarizer(settings: Settings = Depends(get_settings)) -> Summarizer:
    return ClaudeSummarizer(api_key=settings.claude_api_key)


def get_memo_store() -> LocalStorage:
    return LocalStorage()


def get_audio_processor(
    transcriber: Transcriber = Depends(get_transcriber),
) -> AudioProcessor:
    return AudioProcessor(transcriber)


def get_text_processor(
    vectorizer: Vectorizer = Depends(get_vectorizer),
) -> TextProcessor:
    return TextProcessor(vectorizer)


def get_search_engine(
    text_processor: TextProcessor = Depends(get_text_processor),
    vector_storage: VectorStorage = Depends(get_vector_storage),
    storage: Storage = Depends(get_memo_store),
) -> SearchEngine:
    return SearchEngine(text_processor=text_processor, vector_storage=vector_storage, storage=storage)


def get_memo_service(
    audio_processor: AudioProcessor = Depends(get_audio_processor),
    text_processor: TextProcessor = Depends(get_text_processor),
    vector_storage: VectorStorage = Depends(get_vector_storage),
    storage: Storage = Depends(get_memo_store),
    summarizer: Summarizer = Depends(get_summarizer),
) -> MemoService:
    return MemoService(
        audio_processor=audio_processor,
        text_processor=text_processor,
        vector_storage=vector_storage,
        storage=storage,
        summarizer=summarizer,
    )
