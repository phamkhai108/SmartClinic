from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks, HTTPException

from smartclinic.core.ingestion.ingest_controller import (
    _to_response,
    ingest_upload_controller,
)
from smartclinic.core.ingestion.ingest_service import (
    IngestService,
    IngestServiceError,
)
from smartclinic.vectordb.constants import VECTOR_DIMS


@pytest.fixture()
def ingest_service(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "smartclinic.core.files.storage.UPLOAD_ROOT",
        tmp_path,
    )
    repo = MagicMock()
    embed = MagicMock()
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return IngestService(repo, embed, db), repo, embed, db, tmp_path


def test_extension_of():
    assert IngestService.extension_of("doc.PDF") == "pdf"
    assert IngestService.extension_of("noext") == ""
    assert IngestService.extension_of("a.b.Txt") == "txt"


def test_accept_upload_rejects_bad_extension(ingest_service):
    service, *_ = ingest_service
    with pytest.raises(ValueError, match="Unsupported"):
        service.accept_upload(b"data", "note.exe", "u1")


def test_accept_upload_rejects_empty(ingest_service):
    service, *_ = ingest_service
    with pytest.raises(ValueError, match="empty"):
        service.accept_upload(b"", "note.pdf", "u1")


def test_accept_upload_writes_disk_and_pending(ingest_service):
    service, _repo, _embed, db, tmp_path = ingest_service
    row = service.accept_upload(b"hello", "note.pdf", "u1")
    assert row.status == "pending"
    assert row.user_id == "u1"
    assert row.file_name == "note.pdf"
    stored = tmp_path / row.id / "note.pdf"
    assert stored.read_bytes() == b"hello"
    db.add.assert_called_once()
    db.commit.assert_called()


def test_process_file_missing_row(ingest_service):
    service, *_rest = ingest_service
    service._db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(IngestServiceError, match="not found"):
        service.process_file("missing")


def test_process_file_missing_disk_marks_failed(ingest_service):
    service, *_rest = ingest_service
    file_row = SimpleNamespace(id="f1", file_name="a.pdf", status="pending")
    service._db.query.return_value.filter.return_value.first.return_value = file_row
    with pytest.raises(IngestServiceError, match="missing on disk"):
        service.process_file("f1")
    assert file_row.status == "failed"
    service._db.commit.assert_called()


def test_process_file_success_path(ingest_service, monkeypatch):
    service, repo, embed, db, tmp_path = ingest_service
    file_id = "f1"
    path = tmp_path / file_id
    path.mkdir()
    (path / "a.pdf").write_bytes(b"pdf-bytes")

    file_row = SimpleNamespace(id=file_id, file_name="a.pdf", status="pending")
    db.query.return_value.filter.return_value.first.return_value = file_row

    monkeypatch.setattr(
        service,
        "_parse_and_chunk",
        lambda _c, _e, _fid, _fn: [SimpleNamespace(text="chunk-1", headings=())],
    )
    embed.embed_many = MagicMock(return_value=[[0.1] * VECTOR_DIMS])
    service._embed_many = embed.embed_many

    result = service.process_file(file_id)
    assert result.status == "success"
    repo.put.assert_called_once()


def test_process_file_dim_mismatch_cleans_up(ingest_service, monkeypatch):
    service, repo, embed, db, tmp_path = ingest_service
    file_id = "f1"
    path = tmp_path / file_id
    path.mkdir()
    (path / "a.pdf").write_bytes(b"pdf-bytes")
    file_row = SimpleNamespace(id=file_id, file_name="a.pdf", status="pending")
    db.query.return_value.filter.return_value.first.return_value = file_row
    monkeypatch.setattr(
        service,
        "_parse_and_chunk",
        lambda _c, _e, _fid, _fn: [SimpleNamespace(text="chunk-1", headings=())],
    )
    embed.embed_many = MagicMock(return_value=[[0.1, 0.2]])
    service._embed_many = embed.embed_many

    with pytest.raises(IngestServiceError, match="dim mismatch"):
        service.process_file(file_id)
    repo.delete_by_source.assert_called_with(file_id)
    assert file_row.status == "failed"


def test_to_response_unknown_status_becomes_failed():
    dto = _to_response(
        SimpleNamespace(
            id="1",
            user_id="u",
            status="weird",
            file_name="a.pdf",
            created_at=datetime.now(UTC),
        )
    )
    assert dto.status == "failed"


def test_ingest_controller_user_not_found():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    upload = MagicMock()
    upload.filename = "a.pdf"

    async def run():
        with pytest.raises(HTTPException) as exc:
            await ingest_upload_controller(
                upload,
                "missing",
                MagicMock(),
                MagicMock(),
                db,
                BackgroundTasks(),
            )
        return exc.value

    err = asyncio.run(run())
    assert err.status_code == 404


def test_ingest_controller_bad_extension():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = MagicMock()
    upload = MagicMock()
    upload.filename = "a.exe"

    async def run():
        with pytest.raises(HTTPException) as exc:
            await ingest_upload_controller(
                upload,
                "u1",
                MagicMock(),
                MagicMock(),
                db,
                BackgroundTasks(),
            )
        return exc.value

    err = asyncio.run(run())
    assert err.status_code == 400


def test_ingest_controller_empty_upload():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = MagicMock()
    upload = MagicMock()
    upload.filename = "a.pdf"

    async def empty_read():
        return b""

    upload.read = empty_read

    async def run():
        with pytest.raises(HTTPException) as exc:
            await ingest_upload_controller(
                upload,
                "u1",
                MagicMock(),
                MagicMock(),
                db,
                BackgroundTasks(),
            )
        return exc.value

    err = asyncio.run(run())
    assert err.status_code == 400


def test_ingest_controller_schedules_job(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = MagicMock()
    upload = MagicMock()
    upload.filename = "a.pdf"

    async def read_bytes():
        return b"data"

    upload.read = read_bytes
    file_row = SimpleNamespace(
        id="f1",
        user_id="u1",
        status="pending",
        file_name="a.pdf",
        created_at=datetime.now(UTC),
    )
    service = MagicMock()
    service.accept_upload.return_value = file_row
    monkeypatch.setattr(
        "smartclinic.core.ingestion.ingest_controller.build_ingest_service",
        lambda *_a: service,
    )
    bg = BackgroundTasks()

    async def run():
        return await ingest_upload_controller(
            upload,
            "u1",
            MagicMock(),
            MagicMock(),
            db,
            bg,
        )

    result = asyncio.run(run())
    assert result.id == "f1"
    assert result.status == "pending"
    assert len(bg.tasks) == 1
