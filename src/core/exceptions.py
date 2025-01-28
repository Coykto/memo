import logging
from enum import auto, StrEnum
from typing import Any, Dict, Optional


class AppErrorCode(StrEnum):
    """Error codes for the application"""

    INTERNAL_ERROR = auto()
    API_ACCESS_DENIED = auto()
    API_BAD_REQUEST = auto()
    API_RATE_LIMIT_EXCEEDED = auto()
    SUMMARIZATION_FAILED = auto()

    INVALID_AUDIO = auto()
    TRANSCRIPTION_FAILED = auto()
    VECTOR_STORAGE_ERROR = auto()
    MEMO_NOT_FOUND = auto()
    INVALID_USER = auto()
    UNAUTHORIZED = auto()


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

        logging.error(
            message,
            extra={
                "error_code": error_code,
                "status_code": status_code,
                "details": self.details,
            },
        )
        super().__init__(self.message)
