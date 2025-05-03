from datetime import datetime

from pydantic import BaseModel


class FileResponseDTO(BaseModel):
    id: str
    user_id: str
    status: str
    file_name: str
    created_at: datetime
