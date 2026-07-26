from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smartclinic.api.routers import (
    auth,
    brain,
    breast,
    chat,
    chat_history,
    files,
    heart,
    lung,
    mail,
    search,
    user,
)
from smartclinic.common.base import get_settings
from smartclinic.sql.setup_db import setup_db

logger = logging.getLogger("smartclinic")


def configure_logging() -> None:
    """Ensure app loggers emit INFO+ (uvicorn access alone hides chat/SSE internals)."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        root.setLevel(logging.INFO)

    logging.getLogger("smartclinic").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def _setup_vector_backend() -> None:
    settings = get_settings()
    if settings.vector_backend == "elasticsearch":
        if not settings.es_host:
            logger.warning("SMARTCLINIC_ES_HOST not set; vector features unavailable.")
            return
        try:
            from smartclinic.api.dependencies import get_elasticsearch_client
            from smartclinic.vectordb.elasticsearch.es_setup import create_chunk_index

            create_chunk_index(client=get_elasticsearch_client())
        except Exception as exc:
            logger.warning("Elasticsearch index setup skipped: %s", exc)
        return

    if settings.vector_backend == "milvus":
        if not settings.milvus_uri:
            logger.warning("SMARTCLINIC_MILVUS_URI not set; vector features unavailable.")
            return
        try:
            from smartclinic.api.dependencies import get_milvus_client
            from smartclinic.vectordb.milvus.milvus_setup import create_chunks_collection

            create_chunks_collection(client=get_milvus_client())
        except Exception as exc:
            logger.warning("Milvus collection setup skipped: %s", exc)
        return


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info(
        "SmartClinic API starting (vector_backend=%s)",
        get_settings().vector_backend,
    )
    setup_db()
    _setup_vector_backend()
    logger.info("SmartClinic API startup complete")
    yield


app = FastAPI(
    title="SmartClinic API",
    description="Medical AI API with feature-gated services and JWT auth.",
    version="0.2.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brain.router)
app.include_router(breast.router)
app.include_router(heart.router)
app.include_router(lung.router)
app.include_router(chat.router)
app.include_router(chat_history.router)
app.include_router(mail.router)
app.include_router(files.router)
app.include_router(search.router)
app.include_router(auth.router)
app.include_router(user.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("smartclinic.api.main:app", host="localhost", port=8000, reload=True)
