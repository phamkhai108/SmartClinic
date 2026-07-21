from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from smartclinic.vectordb.constants import DEFAULT_VECTOR_BACKEND, VectorBackend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="smartclinic_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    jwt_secret: str = Field(min_length=16)
    jwt_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://localhost:5000"

    sender_email: str | None = None
    sender_password: str | None = None
    vector_backend: VectorBackend = DEFAULT_VECTOR_BACKEND
    es_host: str | None = None
    milvus_uri: str | None = None
    milvus_token: str | None = None
    openai_api_url: str | None = None
    openai_api_key: str | None = None
    model_llm_id: str | None = None
    model_embed_id: str | None = None

    @field_validator(
        "sender_email",
        "sender_password",
        "es_host",
        "milvus_uri",
        "milvus_token",
        "openai_api_url",
        "openai_api_key",
        "model_llm_id",
        "model_embed_id",
        mode="before",
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("vector_backend", mode="before")
    @classmethod
    def normalize_backend(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower() or DEFAULT_VECTOR_BACKEND
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def __getattr__(name: str):
    if name == "AppConfig":
        return get_settings()
    if name == "BaseConfig":
        return Settings
    raise AttributeError(name)
