from datetime import datetime

from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import (
    get_database_client,
    get_elasticsearch_client,
    get_embedding_model,
    get_llm_model,
)
from smartclinic.core.chat.chat_dto import (
    ChatHistoryResponseDto,
    ChatMessageDto,
    ChatResponseDto,
)
from smartclinic.core.chat.chat_service import chat_histories, process_chat
from smartclinic.core.chat_history.chat_history_service import HistoryService
from smartclinic.core.llm.llm_service import LLMModel

router = APIRouter(prefix="/chat_all", tags=["API Chat"])


@router.post("/chat", response_model=ChatResponseDto)
async def chat_endpoint(
    payload: ChatMessageDto,
    llm_model: LLMModel = Depends(get_llm_model),  # noqa: B008
    embedding_model: LLMModel = Depends(get_embedding_model),  # noqa: B008
    client: Elasticsearch = Depends(get_elasticsearch_client),  # noqa: B008
    db: Session = Depends(get_database_client),  # noqa: B008
) -> ChatResponseDto:
    history_service = HistoryService(db)
    return process_chat(
        payload,
        llm_model,
        embedding_model,
        client,
        history_service,
    )


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
