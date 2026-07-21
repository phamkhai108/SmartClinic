from __future__ import annotations

import logging
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

from docling.chunking import HierarchicalChunker
from docling.document_converter import DocumentConverter
from sqlalchemy.orm import Session

from smartclinic.core.ingestion.ingest_constants import (
    ALLOWED_EXTENSIONS,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_SUCCESS,
)
from smartclinic.core.ingestion.ingest_entity import IngestedChunkText
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.sql.setup_db import File
from smartclinic.vectordb.chunk_model import Chunk
from smartclinic.vectordb.constants import VECTOR_DIMS
from smartclinic.vectordb.protocols import ChunkRepository

logger = logging.getLogger(__name__)


class IngestServiceError(Exception):
    """Raised when ingestion fails after optional cleanup."""


class IngestService:
    def __init__(
        self,
        repository: ChunkRepository,
        embedding_model: LLMModel,
        db_session: Session,
        converter: DocumentConverter | None = None,
        chunker: HierarchicalChunker | None = None,
    ) -> None:
        self._repository = repository
        self._embed = embedding_model.embed
        self._db = db_session
        self._converter = converter or DocumentConverter()
        self._chunker = chunker or HierarchicalChunker()

    def ingest_bytes(
        self,
        content: bytes,
        filename: str,
        user_id: str,
    ) -> File:
        extension = self.extension_of(filename)
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '.{extension}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        if not content:
            raise ValueError("Uploaded file is empty.")

        file_row = File(
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_name=filename,
            status=STATUS_PENDING,
            created_at=datetime.now(tz=UTC),
        )
        self._db.add(file_row)
        self._db.commit()
        self._db.refresh(file_row)

        try:
            chunk_texts = self._parse_and_chunk(content, extension)
            if not chunk_texts:
                raise IngestServiceError("No textual chunks extracted from document.")

            now = datetime.now(tz=UTC)
            for item in chunk_texts:
                vector = self._embed(item.text)
                if len(vector) != VECTOR_DIMS:
                    raise IngestServiceError(
                        f"Embedding dim mismatch: got {len(vector)}, "
                        f"expected {VECTOR_DIMS}."
                    )
                self._repository.put(
                    Chunk(
                        id_chunk=str(uuid.uuid4()),
                        chunk_content=item.text,
                        vector_content=vector,
                        status=STATUS_SUCCESS,
                        source=filename,
                        created_at=now,
                        updated_at=now,
                    )
                )

            file_row.status = STATUS_SUCCESS
            self._db.commit()
            self._db.refresh(file_row)
            return file_row
        except Exception as exc:
            logger.exception("Ingestion failed for %s", filename)
            try:
                self._repository.delete_by_source(filename)
            except Exception:
                logger.warning("Cleanup delete_by_source failed for %s", filename)
            file_row.status = STATUS_FAILED
            self._db.commit()
            if isinstance(exc, (IngestServiceError, ValueError)):
                raise
            raise IngestServiceError(str(exc)) from exc

    def _parse_and_chunk(
        self,
        content: bytes,
        extension: str,
    ) -> list[IngestedChunkText]:
        suffix = f".{extension}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = self._converter.convert(tmp_path)
            dl_doc = result.document
            chunks: list[IngestedChunkText] = []
            for chunk in self._chunker.chunk(dl_doc):
                text = self._chunker.contextualize(chunk).strip()
                if not text:
                    continue
                headings = self._extract_headings(chunk)
                chunks.append(IngestedChunkText(text=text, headings=headings))
            return chunks
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @staticmethod
    def _extract_headings(chunk: object) -> tuple[str, ...]:
        meta = getattr(chunk, "meta", None)
        if meta is None:
            return ()
        raw = getattr(meta, "headings", None) or ()
        return tuple(str(h) for h in raw)

    @staticmethod
    def extension_of(filename: str) -> str:
        if "." not in filename:
            return ""
        return filename.rsplit(".", 1)[-1].lower()
