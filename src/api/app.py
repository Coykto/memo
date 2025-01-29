import logging

from anthropic import AnthropicError
from anthropic._exceptions import BadRequestError as AnthropicBadRequestError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAIError
from openai._exceptions import BadRequestError as OpenAIBadRequestError
from pinecone.exceptions import PineconeException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import ValidationError
from starlette.responses import JSONResponse

from src.api.middleware import RequestContextMiddleware
from src.api.routes.memos import router as memos_router
from src.api.routes.search import router as search_router
from src.core.log import setup_logging

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def exception_handling_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logging.error(
                "Unhandled exception",
                extra={
                    "path": request.url.path,
                    "exception_type": exc.__class__.__name__,
                    "exception_message": str(exc),
                },
                exc_info=exc,
            )

            if isinstance(exc, (OpenAIBadRequestError, AnthropicBadRequestError)):
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "Bad request",
                        "detail": str(exc),
                    },
                )

            # Special handling for known API errors
            if isinstance(exc, (OpenAIError, AnthropicError, PineconeException)):
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": "External service error",
                        "detail": str(exc),
                    },
                )

            if isinstance(exc, ValidationError):
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "Bad request",
                        "detail": str(exc),
                    },
                )

            # Generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal server error",
                    "detail": "An unexpected error occurred",
                },
            )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(memos_router)
    app.include_router(search_router)

    Instrumentator().instrument(app).expose(app)
    return app


app = create_app()
