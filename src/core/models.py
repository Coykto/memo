from io import IOBase
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.api.validators import is_non_empty_file


class AudioData(BaseModel):
    """Container for audio data"""

    file: IOBase
    format: Literal[
        "flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"
    ] = Field(description="Audio format e.g., 'wav', 'ogg'")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("file")
    def validate_file(cls, v):
        if not is_non_empty_file(v):
            raise ValueError("Invalid file format")
        return v


class TranscriptionResult(BaseModel):
    text: str


class Summary(BaseModel):
    text: str
    summary: str = Field(max_length=200)


class VectorData(BaseModel):
    """Container for vector data"""

    vector: list[float]
    text: str
    metadata: dict = Field(default_factory=dict)


class Memo(BaseModel):
    """Core memo model"""

    id: str
    text: str
    title: str
    user_id: str
    date: str
    vector: Optional[list[float]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "text": "Remember to buy groceries tomorrow",
                "title": "Shopping reminder",
                "user_id": "user123",
                "date": "2025-02-01T15:31:12.148899",
                "vector": [0.11231, 0.323]
            }
        }
    )


class SearchResult(BaseModel):
    """Container for search result"""

    memo: Memo
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)
