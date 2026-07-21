from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from smartclinic.api.dependencies import create_db_session
from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.chat.chat_dto import (
    ChatHistoryResponseDto,
    ChatMessageDto,
)
from smartclinic.core.chat.chat_service import (
    chat_histories,
    ensure_llm_config,
    format_sse,
    stream_agent_chat,
)
from smartclinic.core.chat_history.chat_history_service import HistoryService

router = APIRouter(prefix="/chat_all", tags=["API Chat"])


@router.post("/chat")
async def chat_endpoint(
    payload: ChatMessageDto,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> StreamingResponse:
    if payload.user_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot chat as another user.",
                "keys": [],
            },
        )

    ensure_llm_config()

    async def event_stream():
        # Own session for stream lifetime (FastAPI <0.118 closes Depends before SSE ends).
        db = create_db_session()
        try:
            history_service = HistoryService(db)
            async for event in stream_agent_chat(payload, history_service):
                yield format_sse(event)
        finally:
            db.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{user_id}", response_model=ChatHistoryResponseDto)
async def get_history(
    user_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    if user_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot view another user's history.",
                "keys": [],
            },
        )
    if user_id not in chat_histories:
        raise HTTPException(status_code=404, detail="User not found")

    history = chat_histories[user_id]
    return ChatHistoryResponseDto(
        user_id=user_id,
        history=history,
        time_at=datetime.now(),
    )
