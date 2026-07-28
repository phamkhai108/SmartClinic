from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from smartclinic.core.files.file_service import FileService


def test_list_files_by_user_all():
    db = MagicMock()
    db.query.return_value.all.return_value = ["a", "b"]
    svc = FileService(db, MagicMock())
    assert svc.list_files_by_user("all") == ["a", "b"]
    db.query.return_value.filter.assert_not_called()


def test_list_files_by_user_filtered():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = ["one"]
    svc = FileService(db, MagicMock())
    assert svc.list_files_by_user("u1") == ["one"]
    db.query.return_value.filter.assert_called_once()


def test_get_file_by_id_404():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    svc = FileService(db, MagicMock())
    with pytest.raises(HTTPException) as exc:
        svc.get_file_by_id("missing")
    assert exc.value.status_code == 404


def test_get_file_by_id_ok():
    db = MagicMock()
    row = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = row
    svc = FileService(db, MagicMock())
    assert svc.get_file_by_id("f1") is row


def test_delete_file_by_id_404():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    svc = FileService(db, MagicMock())
    with pytest.raises(HTTPException) as exc:
        svc.delete_file_by_id("missing")
    assert exc.value.status_code == 404


def test_delete_file_by_id_cleans_vectors_and_disk(monkeypatch):
    db = MagicMock()
    row = MagicMock()
    row.file_name = "legacy.pdf"
    db.query.return_value.filter.return_value.first.return_value = row
    repo = MagicMock()
    removed: list[str] = []
    monkeypatch.setattr(
        "smartclinic.core.files.file_service.remove_stored_file",
        removed.append,
    )
    svc = FileService(db, repo)
    svc.delete_file_by_id("f1")
    assert repo.delete_by_source.call_args_list[0].args == ("f1",)
    assert repo.delete_by_source.call_args_list[1].args == ("legacy.pdf",)
    assert removed == ["f1"]
    db.delete.assert_called_once_with(row)
    db.commit.assert_called_once()
