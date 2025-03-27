from datetime import datetime

from pydantic import BaseModel


class EmailResponse(BaseModel):
    email: str
    code_verify: str
    received_time: datetime = None


class EmailResponseDto(BaseModel):
    email: str
    code_verify: str
    received_time: datetime = None
