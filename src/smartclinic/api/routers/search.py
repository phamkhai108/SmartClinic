from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, Query

from smartclinic.api.dependencies import get_elasticsearch_client, get_embedding_model
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_dto import SearchResultDTO
from smartclinic.core.search.search_service import search_vector_cosine

embeding_model = get_embedding_model()
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/chunks", response_model=SearchResultDTO)
def search_chunks(
    q: str = Query(..., alias="query", description="search chunk in index chunks"),
    size: int = Query(10, ge=1, le=100),
    client: Elasticsearch = Depends(get_elasticsearch_client),  # noqa: B008
    embedding_model: LLMModel = Depends(get_embedding_model),  # noqa: B008
):
    return search_vector_cosine(client, embedding_model, q, size)
