from __future__ import annotations

import pytest
from fastapi import HTTPException

from smartclinic.api.dependencies import (
    require_embed_config,
    require_es_config,
    require_llm_config,
    require_mail_config,
    require_vector_backend_config,
)
from smartclinic.common.base import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _base_env(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")


def test_missing_es_raises_503(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_es_config()
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "MISSING_CONFIG"


def test_missing_llm_lists_keys(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_LLM_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_KEY", "")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_llm_config()
    assert "SMARTCLINIC_LLM_API_URL" in exc.value.detail["keys"]


def test_missing_mail_config(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_SENDER_EMAIL", "")
    monkeypatch.setenv("SMARTCLINIC_SENDER_PASSWORD", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_mail_config()
    assert "SMARTCLINIC_SENDER_EMAIL" in exc.value.detail["keys"]
    assert "SMARTCLINIC_SENDER_PASSWORD" in exc.value.detail["keys"]


def test_missing_embed_config(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_EMBED_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_EMBED_API_KEY", "")
    monkeypatch.setenv("SMARTCLINIC_MODEL_EMBED_ID", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_embed_config()
    assert "SMARTCLINIC_EMBED_API_URL" in exc.value.detail["keys"]
    assert "SMARTCLINIC_MODEL_EMBED_ID" in exc.value.detail["keys"]


def test_vector_backend_requires_es_host(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_VECTOR_BACKEND", "elasticsearch")
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_vector_backend_config()
    assert "SMARTCLINIC_ES_HOST" in exc.value.detail["keys"]


def test_vector_backend_requires_milvus_uri(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("SMARTCLINIC_VECTOR_BACKEND", "milvus")
    monkeypatch.setenv("SMARTCLINIC_MILVUS_URI", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_vector_backend_config()
    assert "SMARTCLINIC_MILVUS_URI" in exc.value.detail["keys"]
