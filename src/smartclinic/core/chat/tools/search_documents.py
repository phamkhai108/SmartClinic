from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from langchain.tools import tool
from langchain_core.tools import BaseTool

from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_service import search_vector_cosine
from smartclinic.vectordb.protocols import ChunkRepository

logger = logging.getLogger(__name__)

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
        logger.info("chat.search.query=%r size=%s", query[:200], SEARCH_SIZE)
        try:
            result = search_vector_cosine(
                repository,
                embedding_model,
                query,
                size=SEARCH_SIZE,
            )
        except Exception as exc:
            logger.exception("chat.search.failed query=%r: %s", query[:200], exc)
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
            logger.info("chat.search.no_hits query=%r", query[:200])
            return json.dumps(
                {"found": False, "message": "No matching documents.", "chunks": []},
                ensure_ascii=False,
            )

        sources: list[str] = []
        chunks: list[dict[str, Any]] = []
        raw_sources: list[str] = []
        for hit in result.hits:
            ref = hit.source or hit.id_chunk
            if ref and ref not in raw_sources:
                raw_sources.append(ref)
            chunks.append(
                {
                    "id": hit.id_chunk,
                    "source": hit.source,
                    "content": hit.chunk_content,
                }
            )

        labels = _resolve_source_labels(raw_sources)
        for ref in raw_sources:
            sources.append(labels.get(ref, ref))

        run_context.sources.clear()
        run_context.sources.extend(sources)

        for chunk in chunks:
            src = chunk.get("source")
            if isinstance(src, str) and src in labels:
                chunk["source"] = labels[src]

        logger.info(
            "chat.search.hits=%s sources=%s",
            len(result.hits),
            sources,
        )

        return json.dumps(
            {"found": True, "sources": sources, "chunks": chunks},
            ensure_ascii=False,
        )

    return search_documents


def _resolve_source_labels(source_ids: list[str]) -> dict[str, str]:
    if not source_ids:
        return {}
    try:
        from smartclinic.api.dependencies import create_db_session
        from smartclinic.sql.setup_db import File
    except Exception:
        return {}

    db = create_db_session()
    try:
        rows = db.query(File).filter(File.id.in_(source_ids)).all()
        return {str(row.id): str(row.file_name) for row in rows}
    except Exception:
        return {}
    finally:
        db.close()
