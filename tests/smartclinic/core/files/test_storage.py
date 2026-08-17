from __future__ import annotations

from pathlib import Path

from smartclinic.core.files.storage import (
    remove_stored_file,
    safe_filename,
    stored_file_path,
)


def test_safe_filename_strips_path_traversal() -> None:
    assert safe_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert ".." not in safe_filename("../a/b/c.docx")


def test_stored_file_path_uses_file_id(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "smartclinic.core.files.storage.UPLOAD_ROOT",
        tmp_path,
    )
    path = stored_file_path("abc-123", "report.pdf")
    assert path == tmp_path / "abc-123" / "report.pdf"


def test_remove_stored_file_deletes_dir(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("smartclinic.core.files.storage.UPLOAD_ROOT", tmp_path)
    target = tmp_path / "fid"
    target.mkdir()
    (target / "a.pdf").write_bytes(b"x")
    remove_stored_file("fid")
    assert not target.exists()
