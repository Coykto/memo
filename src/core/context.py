from contextvars import ContextVar
from typing import Optional
from uuid import uuid4

request_id: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID or generate a new one if none exists"""
    try:
        return request_id.get()
    except LookupError:
        return str(uuid4())


def set_request_id(new_id: Optional[str] = None) -> None:
    """Set request ID for the current context"""
    request_id.set(new_id or str(uuid4()))
