from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from smartclinic.sql.setup_db import File
from smartclinic.vectordb.protocols import ChunkRepository


class FileService:
    def __init__(self, db_session: Session, repository: ChunkRepository) -> None:
        self._db = db_session
        self._repository = repository

    def list_files_by_user(self, user_id: str) -> list[File]:
        if user_id == "all":
            return self._db.query(File).all()
        return self._db.query(File).filter(File.user_id == user_id).all()

    def delete_file_by_filename(self, file_name: str) -> None:
        file_row = self._db.query(File).filter(File.file_name == file_name).first()
        self._repository.delete_by_source(file_name)
        if not file_row:
            raise HTTPException(status_code=404, detail="File not found")
        self._db.delete(file_row)
        self._db.commit()
