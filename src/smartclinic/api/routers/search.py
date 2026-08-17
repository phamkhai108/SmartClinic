from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from smartclinic.api.dependencies import get_chunk_repository, get_embedding_model
from smartclinic.api.deps_auth import CurrentUser, require_roles
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_dto import SearchResultDTO
from smartclinic.core.search.search_service import search_vector_cosine
from smartclinic.vectordb.protocols import ChunkRepository

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/chunks", response_model=SearchResultDTO)
def search_chunks(
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    repository: Annotated[ChunkRepository, Depends(get_chunk_repository)],
    embedding_model: Annotated[LLMModel, Depends(get_embedding_model)],
    q: str = Query(..., alias="query", description="search chunk in index chunks"),
    size: int = Query(10, ge=1, le=100),
) -> SearchResultDTO:
    return search_vector_cosine(repository, embedding_model, q, size)
