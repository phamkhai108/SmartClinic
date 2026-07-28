from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from smartclinic.common.base import Settings
from smartclinic.vectordb.factory import build_chunk_repository


def _settings(**kwargs) -> Settings:
    base = {
        "database_url": "sqlite:///./x.db",
        "jwt_secret": "test-secret-key-16",
    }
    base.update(kwargs)
    return Settings(**base)


def test_build_chunk_repository_requires_es_host():
    with pytest.raises(HTTPException) as exc:
        build_chunk_repository(_settings(vector_backend="elasticsearch", es_host=None))
    assert "SMARTCLINIC_ES_HOST" in exc.value.detail["keys"]


def test_build_chunk_repository_requires_milvus_uri():
    with pytest.raises(HTTPException) as exc:
        build_chunk_repository(_settings(vector_backend="milvus", milvus_uri=None))
    assert "SMARTCLINIC_MILVUS_URI" in exc.value.detail["keys"]


def test_build_chunk_repository_elasticsearch(monkeypatch):
    client = MagicMock(name="es")
    monkeypatch.setattr(
        "elasticsearch.Elasticsearch",
        lambda **_k: client,
    )
    repo = build_chunk_repository(
        _settings(vector_backend="elasticsearch", es_host="http://es")
    )
    assert repo._client is client


def test_build_chunk_repository_milvus(monkeypatch):
    client = MagicMock(name="milvus")
    monkeypatch.setattr(
        "smartclinic.vectordb.factory.create_milvus_client",
        lambda _s: client,
    )
    repo = build_chunk_repository(
        _settings(vector_backend="milvus", milvus_uri="http://milvus")
    )
    assert repo._client is client


def test_build_chunk_repository_unknown_backend(monkeypatch):
    settings = SimpleNamespace(vector_backend="pinecone")
    with pytest.raises(HTTPException) as exc:
        build_chunk_repository(settings)  # type: ignore[arg-type]
    assert "SMARTCLINIC_VECTOR_BACKEND" in exc.value.detail["keys"]
