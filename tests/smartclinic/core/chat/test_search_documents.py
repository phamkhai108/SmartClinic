from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from smartclinic.core.chat.tools.search_documents import (
    _resolve_source_labels,
    build_search_documents_tool,
)
from smartclinic.core.search.search_dto import ChunkResponseDTO, SearchResultDTO


def _hit(source: str = "file-1", content: str = "text") -> ChunkResponseDTO:
    now = datetime.now(UTC)
    return ChunkResponseDTO(
        id_chunk="c1",
        chunk_content=content,
        status="success",
        source=source,
        created_at=now,
        updated_at=now,
    )


def test_search_documents_no_hits(monkeypatch):
    monkeypatch.setattr(
        "smartclinic.core.chat.tools.search_documents.search_vector_cosine",
        lambda *_a, **_k: SearchResultDTO(total=0, hits=[]),
    )
    ctx = SimpleNamespace(sources=["stale"])
    tool = build_search_documents_tool(MagicMock(), MagicMock(), ctx)
    payload = json.loads(tool.invoke({"query": "fever"}))
    assert payload["found"] is False
    assert ctx.sources == []


def test_search_documents_with_hits_updates_sources(monkeypatch):
    monkeypatch.setattr(
        "smartclinic.core.chat.tools.search_documents.search_vector_cosine",
        lambda *_a, **_k: SearchResultDTO(total=1, hits=[_hit("file-1")]),
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.tools.search_documents._resolve_source_labels",
        lambda ids: {ids[0]: "report.pdf"},
    )
    ctx = SimpleNamespace(sources=[])
    tool = build_search_documents_tool(MagicMock(), MagicMock(), ctx)
    payload = json.loads(tool.invoke({"query": "fever"}))
    assert payload["found"] is True
    assert payload["sources"] == ["report.pdf"]
    assert ctx.sources == ["report.pdf"]
    assert payload["chunks"][0]["source"] == "report.pdf"


def test_search_documents_returns_error_json(monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("es down")

    monkeypatch.setattr(
        "smartclinic.core.chat.tools.search_documents.search_vector_cosine",
        boom,
    )
    ctx = SimpleNamespace(sources=[])
    tool = build_search_documents_tool(MagicMock(), MagicMock(), ctx)
    payload = json.loads(tool.invoke({"query": "x"}))
    assert payload["error"] is True
    assert payload["found"] is False


def test_resolve_source_labels_empty():
    assert _resolve_source_labels([]) == {}


def test_resolve_source_labels_maps_file_names(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [
        SimpleNamespace(id="f1", file_name="a.pdf"),
    ]
    monkeypatch.setattr(
        "smartclinic.api.dependencies.create_db_session",
        lambda: db,
    )
    assert _resolve_source_labels(["f1"]) == {"f1": "a.pdf"}
    db.close.assert_called_once()
