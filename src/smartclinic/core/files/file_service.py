import tempfile
import uuid
from datetime import UTC, datetime

import fitz
from docx import Document
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.sql.setup_db import File
from smartclinic.vectordb.elasticsearch.es_model import Chunk
from smartclinic.vectordb.elasticsearch.es_service import Chunker


class UploadFileNProcessChunk:
    def __init__(self, chunker: Chunker, embedding_model: LLMModel, db_session: Session):
        self.chunker = chunker
        self.embedding_model = embedding_model.embed
        self.db_session = db_session

    async def process_and_store_file(self, file: UploadFile, user_id: str) -> File:
        object_meta_file = File(
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_name=file.filename,
            status="pending",
            created_at=datetime.now(tz=UTC),
        )
        self.db_session.add(object_meta_file)
        self.db_session.commit()

        content = await self._extract_text_from_file(file)
        chunks = self._split_text_to_chunks(content)

        for chunk_text in chunks:
            chunk = Chunk(
                id_chunk=str(uuid.uuid4()),
                chunk_content=chunk_text,
                vector_content=self.embedding_model(chunk_text),
                status="pending",
                source=file.filename,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC),
            )
            self.chunker.put(chunk)

        return object_meta_file

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
        self, text: str, max_words: int = 300, overlap: int = 50
    ) -> list[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + max_words]
            chunks.append(" ".join(chunk_words))
            i += max_words - overlap
        return chunks

    def list_files_by_user(self, user_id: str) -> list[File]:
        if user_id == "all":
            return self.db_session.query(File).all()

        # user = self.db_session.query(User).filter(User.id == user_id).first()
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")

        return self.db_session.query(File).filter(File.user_id == user_id).all()

    def delete_file_by_name(self, file_name: str) -> None:
        file = self.db_session.query(File).filter(File.file_name == file_name).first()
        self.chunker.delete_by_source(file_name)

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        self.db_session.delete(file)
        self.db_session.commit()
