from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from elasticsearch import Elasticsearch

from smartclinic.core.search.search_dto import ChunkResponseDTO, SearchResultDTO
from smartclinic.vectordb.chunk_model import Chunk
from smartclinic.vectordb.constants import CHUNKS_COLLECTION, OUTPUT_FIELDS, VECTOR_FIELD


class ElasticsearchChunkRepository:
    def __init__(self, client: Elasticsearch) -> None:
        self._client = client
        self._index = CHUNKS_COLLECTION

    def put(self, chunk: Chunk) -> None:
        self._client.index(
            index=self._index,
            document=chunk.model_dump(mode="json"),
            id=chunk.id_chunk,
        )

    def update(self, chunk: Chunk) -> None:
        self._client.update(
            index=self._index,
            id=chunk.id_chunk,
            body={"doc": chunk.model_dump(mode="json")},
        )

    def delete(self, chunk: Chunk) -> None:
        self._client.delete(index=self._index, id=chunk.id_chunk)

    def delete_by_source(self, source_value: str) -> dict[str, Any]:
        response = self._client.delete_by_query(
            index=self._index,
            body={"query": {"term": {"source": source_value}}},
            refresh=True,
            conflicts="proceed",
        )
        return dict(response)

    def search_cosine(
        self,
        query_vector: Sequence[float],
        size: int = 10,
    ) -> SearchResultDTO:
        body: dict[str, Any] = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{VECTOR_FIELD}')",
                        "params": {"query_vector": list(query_vector)},
                    },
                }
            },
            "size": size,
            "_source": list(OUTPUT_FIELDS),
        }
        response = self._client.search(index=self._index, body=body)
        hits = [ChunkResponseDTO(**hit["_source"]) for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        return SearchResultDTO(total=int(total), hits=hits)


# Backward-compatible alias
Chunker = ElasticsearchChunkRepository
