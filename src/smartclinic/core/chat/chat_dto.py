from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "assistant"] = "user"
    content: str


class choiceMessage(BaseModel):
    messages: list[Message]
    message_id: str
    time_at: datetime
    finish_reason: str


class ChatMessageDto(BaseModel):
    user_id: str
    session_id: str
    messages: list[Message]


class ChatResponseDto(BaseModel):
    user_id: str
    choice: choiceMessage
    history: list[choiceMessage]
    reference: list[str]
    time_at: datetime


class ChatHistoryResponseDto(BaseModel):
    user_id: str
    history: list[choiceMessage]
    time_at: datetime
