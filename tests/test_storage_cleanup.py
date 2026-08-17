from __future__ import annotations

from pathlib import Path

from smartclinic.core.files.storage import remove_stored_file


def test_remove_stored_file_deletes_dir(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("smartclinic.core.files.storage.UPLOAD_ROOT", tmp_path)
    target = tmp_path / "fid"
    target.mkdir()
    (target / "a.pdf").write_bytes(b"x")
    remove_stored_file("fid")
    assert not target.exists()
