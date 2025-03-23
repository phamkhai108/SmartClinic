from datetime import datetime

from pydantic import BaseModel


class EmailResponselDto(BaseModel):
    email: str
    code_verify: str
    received_time: datetime = None
