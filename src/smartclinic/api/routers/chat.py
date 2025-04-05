# app/router.py

from datetime import datetime

from fastapi import APIRouter, HTTPException

from smartclinic.core.chat.chat_dto import (
    ChatHistoryResponseDto,
    ChatMessageDto,
    ChatResponseDto,
)
from smartclinic.core.chat.chat_service import chat_histories, process_chat

router = APIRouter(prefix="/chat_all", tags=["API Chat"])


@router.post("/chat", response_model=ChatResponseDto)
async def chat_endpoint(payload: ChatMessageDto) -> ChatResponseDto:
    return process_chat(payload)


@router.get("/history/{user_id}", response_model=ChatHistoryResponseDto)
async def get_history(user_id: str):
    if user_id not in chat_histories:
        raise HTTPException(status_code=404, detail="User not found")

    history = chat_histories[user_id]

    return ChatHistoryResponseDto(
        user_id=user_id,
        history=history,
        time_at=datetime.now(),
    )
