from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from smartclinic.core.ingestion.ingest_constants import FileIngestStatus


class IngestFileResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    status: FileIngestStatus
    file_name: str
    created_at: datetime
