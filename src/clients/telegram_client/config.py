from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    telegram_api_token: str
    templates_folder: Path = Path(__file__).parent / "templates"
    api_base_url: str
    
    class Config:
        env_file = Path(__file__).parent / ".env"


settings = Settings()
