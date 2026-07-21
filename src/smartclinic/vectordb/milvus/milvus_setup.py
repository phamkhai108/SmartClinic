from __future__ import annotations

from pymilvus import DataType, MilvusClient

from smartclinic.vectordb.constants import (
    CHUNKS_COLLECTION,
    VECTOR_DIMS,
    VECTOR_FIELD,
)


def create_chunks_collection(client: MilvusClient) -> None:
    if client.has_collection(collection_name=CHUNKS_COLLECTION):
        return

    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
    schema.add_field(
        field_name="id_chunk",
        datatype=DataType.VARCHAR,
        is_primary=True,
        max_length=64,
    )
    schema.add_field(
        field_name="chunk_content",
        datatype=DataType.VARCHAR,
        max_length=65535,
    )
    schema.add_field(
        field_name=VECTOR_FIELD,
        datatype=DataType.FLOAT_VECTOR,
        dim=VECTOR_DIMS,
    )
    schema.add_field(field_name="status", datatype=DataType.VARCHAR, max_length=16)
    schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=512)
    schema.add_field(field_name="created_at", datatype=DataType.VARCHAR, max_length=64)
    schema.add_field(field_name="updated_at", datatype=DataType.VARCHAR, max_length=64)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name=VECTOR_FIELD,
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )

    client.create_collection(
        collection_name=CHUNKS_COLLECTION,
        schema=schema,
        index_params=index_params,
    )
