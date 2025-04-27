import tempfile
import uuid
from datetime import UTC, datetime

import fitz
from docx import Document
from fastapi import UploadFile

# ollama_nomic = LLMModel(
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.vectordb.elasticsearch.es_model import Chunk
from smartclinic.vectordb.elasticsearch.es_service import Chunker


class FileProcessingService:
    def __init__(self, chunker: Chunker, embedding_model: LLMModel):
        self.chunker = chunker
        self.embedding_model = embedding_model.embed

    async def process_and_store_file(self, file: UploadFile) -> int:
        content = await self._extract_text_from_file(file)

        chunks = self._split_text_to_chunks(content)

        now = datetime.now(tz=UTC)

        for chunk_text in chunks:
            chunk = Chunk(
                id_chunk=str(uuid.uuid4()),
                chunk_content=chunk_text,
                vector_content=self.embedding_model(chunk_text),
                status="pending",
                source=file.filename,
                created_at=now,
                updated_at=now,
            )
            self.chunker.put(chunk)

        return len(chunks)

    async def _extract_text_from_file(self, file: UploadFile) -> str:
        suffix = file.filename.lower().split(".")[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix="." + suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        if suffix == "pdf":
            return self._extract_text_from_pdf(tmp_path)
        elif suffix == "docx":
            return self._extract_text_from_docx(tmp_path)
        else:
            raise ValueError("Unsupported file format")

    def _extract_text_from_pdf(self, path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _extract_text_from_docx(self, path: str) -> str:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    def _split_text_to_chunks(
        self, text: str, max_words: int = 300, overlap: int = 70
    ) -> list[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + max_words]
            chunks.append(" ".join(chunk_words))
            i += max_words - overlap
        return chunks
