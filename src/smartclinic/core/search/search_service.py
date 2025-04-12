from elasticsearch import Elasticsearch

from smartclinic.core.search.search_dto import ChunkResponseDTO, SearchResultDTO


def search_fulltext(client: Elasticsearch, query: str, size: int = 10) -> SearchResultDTO:
    body = {
        "query": {"match": {"chunk_content": query}},
        "size": size,
        "_source": [
            "id_chunk",
            "chunk_content",
            "status",
            "source",
            "created_at",
            "updated_at",
        ],
    }

    response = client.search(index="chunks", body=body)

    hits = [ChunkResponseDTO(**hit["_source"]) for hit in response["hits"]["hits"]]
    return SearchResultDTO(total=response["hits"]["total"]["value"], hits=hits)


# es_client = Elasticsearch(
#     hosts="http://localhost:9200", request_timeout=30, max_retries=2
# )

# result = search_fulltext(es_client, "This is a chunk")
# print(result.model_dump_json(indent=2))
