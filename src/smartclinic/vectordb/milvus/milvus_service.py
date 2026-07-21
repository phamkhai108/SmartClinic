from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from pymilvus import MilvusClient

from smartclinic.core.search.search_dto import ChunkResponseDTO, SearchResultDTO
from smartclinic.vectordb.chunk_model import Chunk
from smartclinic.vectordb.constants import (
    CHUNKS_COLLECTION,
    OUTPUT_FIELDS,
    VECTOR_FIELD,
)


def _escape_filter_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _entity_to_dto(entity: Mapping[str, Any]) -> ChunkResponseDTO:
    return ChunkResponseDTO(
        id_chunk=str(entity["id_chunk"]),
        chunk_content=str(entity["chunk_content"]),
        status=str(entity["status"]),
        source=str(entity["source"]),
        created_at=_parse_datetime(entity["created_at"]),
        updated_at=_parse_datetime(entity["updated_at"]),
    )


def _chunk_to_row(chunk: Chunk) -> dict[str, Any]:
    return {
        "id_chunk": chunk.id_chunk,
        "chunk_content": chunk.chunk_content,
        VECTOR_FIELD: list(chunk.vector_content),
        "status": chunk.status,
        "source": chunk.source,
        "created_at": chunk.created_at.isoformat(),
        "updated_at": chunk.updated_at.isoformat(),
    }


class MilvusChunkRepository:
    def __init__(self, client: MilvusClient) -> None:
        self._client = client
        self._collection = CHUNKS_COLLECTION

    def put(self, chunk: Chunk) -> None:
        self._client.upsert(
            collection_name=self._collection,
            data=[_chunk_to_row(chunk)],
        )

    def update(self, chunk: Chunk) -> None:
        self.put(chunk)

    def delete(self, chunk: Chunk) -> None:
        self._client.delete(
            collection_name=self._collection,
            ids=[chunk.id_chunk],
        )

    def delete_by_source(self, source_value: str) -> dict[str, Any]:
        escaped = _escape_filter_value(source_value)
        result = self._client.delete(
            collection_name=self._collection,
            filter=f'source == "{escaped}"',
        )
        if isinstance(result, dict):
            return result
        return {"result": result}

    def search_cosine(
        self,
        query_vector: Sequence[float],
        size: int = 10,
    ) -> SearchResultDTO:
        raw = self._client.search(
            collection_name=self._collection,
            data=[list(query_vector)],
            anns_field=VECTOR_FIELD,
            limit=size,
            output_fields=list(OUTPUT_FIELDS),
            search_params={"metric_type": "COSINE"},
        )
        hits_group = raw[0] if raw else []
        hits: list[ChunkResponseDTO] = []
        for item in hits_group:
            entity = item.get("entity") or item
            hits.append(_entity_to_dto(entity))
        return SearchResultDTO(total=len(hits), hits=hits)
