from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Chunk(BaseModel):
    id_chunk: str
    chunk_content: str
    vector_content: list[float]
    status: Literal["pending", "success", "failed"]
    source: str
    created_at: datetime
    updated_at: datetime
