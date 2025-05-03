from elasticsearch import Elasticsearch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from smartclinic.common.base import AppConfig
from smartclinic.core.llm.llm_service import LLMModel


def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(hosts=AppConfig.es_host, request_timeout=30, max_retries=2)


def get_embedding_model() -> LLMModel:
    return LLMModel(
        openai_api_url=AppConfig.openai_api_url,
        openai_api_key=AppConfig.openai_api_key,
        model_id=AppConfig.model_embed_id,
    )


def get_llm_model() -> LLMModel:
    return LLMModel(
        openai_api_url=AppConfig.openai_api_url,
        openai_api_key=AppConfig.openai_api_key,
        model_id=AppConfig.model_llm_id,
    )


engine = create_engine(
    AppConfig.database_url,
    connect_args={"check_same_thread": False}
    if AppConfig.database_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_client() -> Session:
    return SessionLocal()
