from datetime import datetime

from pydantic import BaseModel


class EmailResponseDTO(BaseModel):
    email: str
    code_verify: str
    received_time: datetime = None


class EmailRequestDTO(BaseModel):
    receiver_email: str
