from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    pinecone_host: str
    claude_api_key: str

    model_config = ConfigDict(env_file=Path(__file__).parent / ".env")
