from __future__ import annotations

from collections.abc import Generator

from elasticsearch import Elasticsearch
from pymilvus import MilvusClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from smartclinic.common.base import Settings, get_settings
from smartclinic.common.errors import feature_unavailable_error, missing_config_error
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.mailer.email_service import EmailService
from smartclinic.vectordb.factory import build_chunk_repository
from smartclinic.vectordb.milvus.milvus_client import create_milvus_client
from smartclinic.vectordb.protocols import ChunkRepository

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False}
            if settings.database_url.startswith("sqlite")
            else {},
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def create_db_session() -> Session:
    _get_engine()
    assert _SessionLocal is not None
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    db = create_db_session()
    try:
        yield db
    finally:
        db.close()


def require_mail_config() -> None:
    s = get_settings()
    missing: list[str] = []
    if not s.sender_email:
        missing.append("SMARTCLINIC_SENDER_EMAIL")
    if not s.sender_password:
        missing.append("SMARTCLINIC_SENDER_PASSWORD")
    if missing:
        raise missing_config_error(missing)


def require_vector_backend_config(settings: Settings | None = None) -> None:
    s = settings or get_settings()
    if s.vector_backend == "elasticsearch" and not s.es_host:
        raise missing_config_error(["SMARTCLINIC_ES_HOST"])
    if s.vector_backend == "milvus" and not s.milvus_uri:
        raise missing_config_error(["SMARTCLINIC_MILVUS_URI"])


def require_es_config() -> None:
    if not get_settings().es_host:
        raise missing_config_error(["SMARTCLINIC_ES_HOST"])


def require_llm_config() -> None:
    s = get_settings()
    missing: list[str] = []
    if not s.resolved_llm_api_url:
        missing.append("SMARTCLINIC_LLM_API_URL")
    if not s.resolved_llm_api_key:
        missing.append("SMARTCLINIC_LLM_API_KEY")
    if not s.model_llm_id:
        missing.append("SMARTCLINIC_MODEL_LLM_ID")
    if missing:
        raise missing_config_error(missing)


def require_embed_config() -> None:
    s = get_settings()
    missing: list[str] = []
    if not s.resolved_embed_api_url:
        missing.append("SMARTCLINIC_EMBED_API_URL")
    if not s.resolved_embed_api_key:
        missing.append("SMARTCLINIC_EMBED_API_KEY")
    if not s.model_embed_id:
        missing.append("SMARTCLINIC_MODEL_EMBED_ID")
    if missing:
        raise missing_config_error(missing)


def get_elasticsearch_client() -> Elasticsearch:
    require_es_config()
    try:
        return Elasticsearch(
            hosts=get_settings().es_host,
            request_timeout=30,
            max_retries=2,
        )
    except Exception as exc:
        raise feature_unavailable_error(f"Elasticsearch unavailable: {exc}") from exc


def get_milvus_client() -> MilvusClient:
    settings = get_settings()
    if not settings.milvus_uri:
        raise missing_config_error(["SMARTCLINIC_MILVUS_URI"])
    try:
        return create_milvus_client(settings)
    except Exception as exc:
        raise feature_unavailable_error(f"Milvus unavailable: {exc}") from exc


def get_chunk_repository() -> ChunkRepository:
    require_vector_backend_config()
    return build_chunk_repository(get_settings())


def get_embedding_model() -> LLMModel:
    require_embed_config()
    s = get_settings()
    return LLMModel(
        openai_api_url=s.resolved_embed_api_url,
        openai_api_key=s.resolved_embed_api_key,
        model_id=s.model_embed_id,
    )


def get_llm_model() -> LLMModel:
    require_llm_config()
    s = get_settings()
    return LLMModel(
        openai_api_url=s.resolved_llm_api_url,
        openai_api_key=s.resolved_llm_api_key,
        model_id=s.model_llm_id,
    )


def get_mailer_service() -> EmailService:
    require_mail_config()
    s = get_settings()
    return EmailService(
        sender_email=s.sender_email,
        sender_password=s.sender_password,
    )
