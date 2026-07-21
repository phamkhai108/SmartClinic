from __future__ import annotations

from typing import Final, Literal

FileIngestStatus = Literal["pending", "success", "failed"]
ChunkIngestStatus = Literal["pending", "success", "failed"]

ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        "pdf",
        "docx",
        "xlsx",
        "pptx",
        "md",
        "markdown",
    }
)

STATUS_PENDING: Final[FileIngestStatus] = "pending"
STATUS_SUCCESS: Final[FileIngestStatus] = "success"
STATUS_FAILED: Final[FileIngestStatus] = "failed"
