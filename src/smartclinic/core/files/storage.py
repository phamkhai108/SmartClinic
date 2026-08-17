from __future__ import annotations

import re
from contextlib import suppress
from pathlib import Path

UPLOAD_ROOT = Path("./uploaded_files")

_SAFE_NAME = re.compile(r"[^\w.\-()+ ]+", re.UNICODE)


def safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "upload.bin"
    cleaned = _SAFE_NAME.sub("_", name).strip("._") or "upload.bin"
    return cleaned[:200]


def file_dir(file_id: str) -> Path:
    return UPLOAD_ROOT / file_id


def stored_file_path(file_id: str, filename: str) -> Path:
    return file_dir(file_id) / safe_filename(filename)


def converted_md_path(file_id: str, filename: str) -> Path:
    stem = Path(safe_filename(filename)).stem
    return file_dir(file_id) / f"{stem}.md"


def ensure_upload_root() -> None:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def remove_stored_file(file_id: str) -> None:
    directory = file_dir(file_id)
    if not directory.exists():
        return
    for child in directory.iterdir():
        if child.is_file():
            child.unlink(missing_ok=True)
    with suppress(OSError):
        directory.rmdir()
