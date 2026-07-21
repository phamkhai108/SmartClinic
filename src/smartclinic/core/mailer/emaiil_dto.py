from datetime import datetime

from pydantic import BaseModel


class EmailResponseDTO(BaseModel):
    email: str | None = None
    code_verify: str | None = None
    received_time: datetime | None = None


class EmailRequestDTO(BaseModel):
    receiver_email: str
