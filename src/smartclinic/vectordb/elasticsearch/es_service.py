from datetime import datetime
from uuid import uuid4

from elasticsearch import Elasticsearch

from smartclinic.vectordb.elasticsearch.es_model import Chunk


class Chunker:
    def __init__(self, client: Elasticsearch):
        self.client = client
        self.index_name = "chunks"

    def put(self, chunk: Chunk) -> None:
        doc = chunk.model_dump()
        self.client.index(index=self.index_name, document=doc, id=str(chunk.id_chunk))

    def update(self, chunk: Chunk) -> None:
        doc = {"doc": chunk.model_dump()}
        self.client.update(index=self.index_name, id=str(chunk.id_chunk), body=doc)

    def delete(self, chunk: Chunk) -> None:
        self.client.delete(index=self.index_name, id=str(chunk.id_chunk))


# client = Elasticsearch(hosts="http://localhost:9200", request_timeout=30, max_retries=2)

# chunk_repo = Chunker(client)

# chunk = Chunk(
#     id_chunk=str(uuid4()),
#     chunk_content="Tôi tên là khải",
#     vector_content=[float(i) for i in range(1024)],
#     status="pending",
#     source="source_test",
#     created_at=datetime.now(),
#     updated_at=datetime.now(),
# )

# chunk_repo.put(chunk)  # Put data vào index
# chunk_repo.update(chunk)  # Update data trong index
# chunk_repo.delete(chunk)  # Delete data khỏi index
