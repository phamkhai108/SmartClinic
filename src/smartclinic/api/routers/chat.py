# app/router.py

from datetime import datetime

from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.dependencies import get_elasticsearch_client
from smartclinic.common import AppConfig
from smartclinic.core.chat.chat_dto import (
    ChatHistoryResponseDto,
    ChatMessageDto,
    ChatResponseDto,
)
from smartclinic.core.chat.chat_service import chat_histories, process_chat
from smartclinic.core.llm.llm_service import LLMModel

router = APIRouter(prefix="/chat_all", tags=["API Chat"])

embedding_model = LLMModel(
    openai_api_url=AppConfig.openai_api_url,
    openai_api_key=AppConfig.openai_api_key,
    model_id=AppConfig.model_llm_id,
)


@router.post("/chat", response_model=ChatResponseDto)
async def chat_endpoint(
    payload: ChatMessageDto,
    client: Elasticsearch = Depends(get_elasticsearch_client),  # noqa: B008
) -> ChatResponseDto:
    return process_chat(payload, embedding_model, client=client)


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
