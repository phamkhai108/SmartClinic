from datetime import datetime

from pydantic import BaseModel


class SessionInfo(BaseModel):
    session_id: str
    conversation_name: str
    latest_timestamp: datetime


class ChatMessageSchema(BaseModel):
    id: str
    session_id: str
    user_id: str
    conversation_name: str
    message: str
    sender: str
    timestamp: datetime

    class Config:
        orm_mode = True
