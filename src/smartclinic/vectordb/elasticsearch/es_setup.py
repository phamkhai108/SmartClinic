from elasticsearch import Elasticsearch


def create_chunk_index(client: Elasticsearch) -> None:
    index_name = "chunks"
    vector_dims = 384

    mapping = {
        "mappings": {
            "properties": {
                "id_chunk": {"type": "keyword"},
                "chunk_content": {"type": "text"},
                "vector_content": {"type": "dense_vector", "dims": vector_dims},
                "status": {"type": "keyword"},
                "source": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }

    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=mapping)
