from datetime import datetime

from pydantic import BaseModel


class ChunkResponseDTO(BaseModel):
    id_chunk: str
    chunk_content: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime


class SearchResultDTO(BaseModel):
    total: int
    hits: list[ChunkResponseDTO]
