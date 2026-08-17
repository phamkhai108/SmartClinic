from __future__ import annotations

from contextlib import suppress

from fastapi import HTTPException
from sqlalchemy.orm import Session

from smartclinic.core.files.storage import remove_stored_file
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

    def get_file_by_id(self, file_id: str) -> File:
        file_row = self._db.query(File).filter(File.id == file_id).first()
        if not file_row:
            raise HTTPException(status_code=404, detail="File not found")
        return file_row

    def delete_file_by_id(self, file_id: str) -> None:
        file_row = self._db.query(File).filter(File.id == file_id).first()
        if not file_row:
            raise HTTPException(status_code=404, detail="File not found")

        self._repository.delete_by_source(file_id)
        # Legacy chunks may still use original filename as source.
        if file_row.file_name:
            with suppress(Exception):
                self._repository.delete_by_source(str(file_row.file_name))

        remove_stored_file(file_id)
        self._db.delete(file_row)
        self._db.commit()
