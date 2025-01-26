from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from log import setup_logging
from src.api.routes.memos import router as memos_router
from src.api.routes.search import router as search_router

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI()

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
