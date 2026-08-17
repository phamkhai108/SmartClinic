from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi import (
    File as UploadFileParam,
)
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import (
    get_chunk_repository,
    get_db,
    get_embedding_model,
)
from smartclinic.api.deps_auth import CurrentUser, require_roles
from smartclinic.core.files.file_dto import FileResponseDTO
from smartclinic.core.files.file_service import FileService
from smartclinic.core.files.storage import ensure_upload_root
from smartclinic.core.ingestion.ingest_controller import ingest_upload_controller
from smartclinic.core.ingestion.ingest_dto import IngestFileResponseDTO
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.sql.setup_db import File as FileEntity
from smartclinic.vectordb.protocols import ChunkRepository

ensure_upload_root()

router = APIRouter(prefix="/files", tags=["File Management"])


@router.post(
    "/upload_flow",
    response_model=IngestFileResponseDTO,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file(
    user_id: str,
    background_tasks: BackgroundTasks,
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    repository: Annotated[ChunkRepository, Depends(get_chunk_repository)],
    embedding_model: Annotated[LLMModel, Depends(get_embedding_model)],
    file: Annotated[UploadFile, UploadFileParam()],
) -> IngestFileResponseDTO:
    return await ingest_upload_controller(
        upload=file,
        user_id=user_id,
        repository=repository,
        embedding_model=embedding_model,
        db=db,
        background_tasks=background_tasks,
    )


@router.get("/get_info_files", response_model=list[FileResponseDTO])
def list_files_by_user(
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    user_id: str = Query(..., description='User ID or "all"'),
) -> list[FileEntity]:
    try:
        if user_id == "all":
            return db.query(FileEntity).all()
        return db.query(FileEntity).filter(FileEntity.user_id == user_id).all()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{file_id}", response_model=FileResponseDTO)
def get_file(
    file_id: str,
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> FileEntity:
    file_row = db.query(FileEntity).filter(FileEntity.id == file_id).first()
    if not file_row:
        raise HTTPException(status_code=404, detail="File not found")
    return file_row


@router.delete("/delete_file/{file_id}")
async def delete_file(
    file_id: str,
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    repository: Annotated[ChunkRepository, Depends(get_chunk_repository)],
) -> dict[str, str]:
    try:
        FileService(db, repository).delete_file_by_id(file_id)
        return {
            "detail": f"File {file_id} deleted successfully.",
            "status": "success",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
