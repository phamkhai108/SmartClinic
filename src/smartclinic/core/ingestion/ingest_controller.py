from __future__ import annotations

from typing import cast

from fastapi import BackgroundTasks, HTTPException, UploadFile
from sqlalchemy.orm import Session

from smartclinic.core.ingestion.ingest_constants import (
    ALLOWED_EXTENSIONS,
    FileIngestStatus,
)
from smartclinic.core.ingestion.ingest_dto import IngestFileResponseDTO
from smartclinic.core.ingestion.ingest_service import (
    IngestService,
    run_ingest_job,
)
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.vectordb.protocols import ChunkRepository


def build_ingest_service(
    repository: ChunkRepository,
    embedding_model: LLMModel,
    db: Session,
) -> IngestService:
    return IngestService(
        repository=repository,
        embedding_model=embedding_model,
        db_session=db,
    )


def _to_response(file_row) -> IngestFileResponseDTO:
    raw_status = str(file_row.status)
    status: FileIngestStatus
    if raw_status in ("pending", "success", "failed"):
        status = cast(FileIngestStatus, raw_status)
    else:
        status = "failed"

    return IngestFileResponseDTO(
        id=str(file_row.id),
        user_id=str(file_row.user_id),
        status=status,
        file_name=str(file_row.file_name),
        created_at=file_row.created_at,
    )


async def ingest_upload_controller(
    upload: UploadFile,
    user_id: str,
    repository: ChunkRepository,
    embedding_model: LLMModel,
    db: Session,
    background_tasks: BackgroundTasks,
) -> IngestFileResponseDTO:
    filename = upload.filename or ""
    extension = IngestService.extension_of(filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    content = await upload.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # repository / embedding_model validated by Depends before this runs;
    # accept_upload itself only needs DB + disk.
    service = build_ingest_service(repository, embedding_model, db)
    try:
        file_row = service.accept_upload(content, filename, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error accepting file: {exc}",
        ) from exc

    background_tasks.add_task(run_ingest_job, str(file_row.id))
    return _to_response(file_row)
