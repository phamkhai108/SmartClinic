from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from smartclinic.api.dependencies import create_db_session
from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.chat.chat_dto import ChatMessageDto
from smartclinic.core.chat.chat_service import (
    ensure_llm_config,
    format_sse,
    stream_agent_chat,
)
from smartclinic.core.chat_history.chat_history_service import HistoryService

logger = logging.getLogger(__name__)

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
    logger.info(
        "chat.http_accept session=%s user=%s (SSE 200 starts before stream finishes)",
        payload.session_id,
        payload.user_id,
    )

    async def event_stream():
        # Own session for stream lifetime (FastAPI <0.118 closes Depends before SSE ends).
        db = create_db_session()
        try:
            history_service = HistoryService(db)
            async for event in stream_agent_chat(payload, history_service):
                event_type = event.get("type")
                if event_type in {"error", "done"}:
                    logger.info(
                        "chat.sse_event type=%s session=%s",
                        event_type,
                        payload.session_id,
                    )
                yield format_sse(event)
        except Exception:
            logger.exception(
                "chat.stream_aborted session=%s user=%s",
                payload.session_id,
                payload.user_id,
            )
            raise
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
