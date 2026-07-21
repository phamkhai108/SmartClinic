from __future__ import annotations

from typing import Final, Literal

VECTOR_DIMS: Final[int] = 1536
CHUNKS_COLLECTION: Final[str] = "chunks"
VECTOR_FIELD: Final[str] = "vector_content"

VectorBackend = Literal["elasticsearch", "milvus"]

DEFAULT_VECTOR_BACKEND: Final[VectorBackend] = "elasticsearch"

OUTPUT_FIELDS: Final[tuple[str, ...]] = (
    "id_chunk",
    "chunk_content",
    "status",
    "source",
    "created_at",
    "updated_at",
)
