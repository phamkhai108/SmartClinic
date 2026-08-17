from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionInfo(BaseModel):
    session_id: str
    conversation_name: str
    latest_timestamp: datetime


class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    user_id: str
    conversation_name: str
    message: str
    sender: str
    timestamp: datetime
