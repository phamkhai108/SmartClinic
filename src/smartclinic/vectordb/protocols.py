from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from smartclinic.core.search.search_dto import SearchResultDTO
from smartclinic.vectordb.chunk_model import Chunk


class ChunkRepository(Protocol):
    def put(self, chunk: Chunk) -> None: ...

    def update(self, chunk: Chunk) -> None: ...

    def delete(self, chunk: Chunk) -> None: ...

    def delete_by_source(self, source_value: str) -> dict[str, Any]: ...

    def search_cosine(
        self,
        query_vector: Sequence[float],
        size: int = 10,
    ) -> SearchResultDTO: ...
