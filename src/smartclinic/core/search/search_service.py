from elasticsearch import Elasticsearch

from smartclinic.core.llm.llm_service import LLMModel
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


def search_vector_cosine(
    client: Elasticsearch,
    embedding_model: LLMModel,
    query: str,
    size: int = 10,
) -> SearchResultDTO:
    body = {
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector_content')",
                    "params": {"query_vector": embedding_model.embed(query)},
                },
            }
        },
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
