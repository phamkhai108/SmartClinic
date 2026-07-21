from __future__ import annotations

import json
from typing import Any, Protocol

from langchain.tools import tool
from langchain_core.tools import BaseTool

from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_service import search_vector_cosine
from smartclinic.vectordb.protocols import ChunkRepository

SEARCH_SIZE: int = 4


class SearchRunContext(Protocol):
    sources: list[str]


def build_search_documents_tool(
    repository: ChunkRepository,
    embedding_model: LLMModel,
    run_context: SearchRunContext,
) -> BaseTool:
    @tool("search_documents")
    def search_documents(query: str) -> str:
        """Search internal clinic documents by semantic similarity.

        Args:
            query: Natural language search query about medical content.
        """
        try:
            result = search_vector_cosine(
                repository,
                embedding_model,
                query,
                size=SEARCH_SIZE,
            )
        except Exception as exc:
            return json.dumps(
                {
                    "found": False,
                    "error": True,
                    "message": (
                        "Document search is temporarily unavailable. "
                        f"Continue without documents. Detail: {exc}"
                    ),
                    "chunks": [],
                },
                ensure_ascii=False,
            )

        if not result.hits:
            run_context.sources.clear()
            return json.dumps(
                {"found": False, "message": "No matching documents.", "chunks": []},
                ensure_ascii=False,
            )

        sources: list[str] = []
        chunks: list[dict[str, Any]] = []
        for hit in result.hits:
            ref = hit.source or hit.id_chunk
            if ref and ref not in sources:
                sources.append(ref)
            chunks.append(
                {
                    "id": hit.id_chunk,
                    "source": hit.source,
                    "content": hit.chunk_content,
                }
            )

        run_context.sources.clear()
        run_context.sources.extend(sources)

        return json.dumps(
            {"found": True, "sources": sources, "chunks": chunks},
            ensure_ascii=False,
        )

    return search_documents
