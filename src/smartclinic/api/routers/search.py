from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, Query

from smartclinic.api.dependencies import get_elasticsearch_client
from smartclinic.core.search.search_dto import SearchResultDTO
from smartclinic.core.search.search_service import search_fulltext

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/chunks", response_model=SearchResultDTO)
def search_chunks(
    q: str = Query(..., alias="query", description="search chunk in index chunks"),
    size: int = Query(10, ge=1, le=100),
    client: Elasticsearch = Depends(get_elasticsearch_client),  # noqa: B008
):
    return search_fulltext(client, q, size)
