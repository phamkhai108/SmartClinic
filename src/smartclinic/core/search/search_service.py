from __future__ import annotations

from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_dto import SearchResultDTO
from smartclinic.vectordb.protocols import ChunkRepository


def search_vector_cosine(
    repository: ChunkRepository,
    embedding_model: LLMModel,
    query: str,
    size: int = 10,
) -> SearchResultDTO:
    query_vector = embedding_model.embed(query)
    return repository.search_cosine(query_vector, size)
