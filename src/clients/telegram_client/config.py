from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_api_token: str
    templates_folder: Path = Path(__file__).parent / "templates"
    api_base_url: str

    model_config = ConfigDict(env_file=Path(__file__).parent / ".env")


settings = Settings()
