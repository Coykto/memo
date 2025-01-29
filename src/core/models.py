from io import IOBase
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class AudioData(BaseModel):
    """Container for audio data"""

    file: IOBase
    format: Literal[
        "flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"
    ] = Field(description="Audio format e.g., 'wav', 'ogg'")

    model_config = ConfigDict(arbitrary_types_allowed=True)


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
    vector: Optional[list[float]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "text": "Remember to buy groceries tomorrow",
                "title": "Shopping reminder",
                "user_id": "user123",
            }
        }
    )


class SearchResult(BaseModel):
    """Container for search result"""

    memo: Memo
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)
