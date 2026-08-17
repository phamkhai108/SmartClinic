from __future__ import annotations

from elasticsearch import Elasticsearch

from smartclinic.vectordb.constants import CHUNKS_COLLECTION, VECTOR_DIMS, VECTOR_FIELD


def create_chunk_index(client: Elasticsearch) -> None:
    mapping: dict = {
        "mappings": {
            "properties": {
                "id_chunk": {"type": "keyword"},
                "chunk_content": {"type": "text"},
                VECTOR_FIELD: {"type": "dense_vector", "dims": VECTOR_DIMS},
                "status": {"type": "keyword"},
                "source": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }
    if not client.indices.exists(index=CHUNKS_COLLECTION):
        client.indices.create(index=CHUNKS_COLLECTION, body=mapping)
