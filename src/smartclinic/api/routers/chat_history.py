from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_db
from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.chat_history.chat_history_dto import ChatMessageSchema, SessionInfo
from smartclinic.core.chat_history.chat_history_service import HistoryService

router = APIRouter(prefix="/chat_history", tags=["Chat history"])


@router.get("/chat_sessions/{user_id}", response_model=list[SessionInfo])
def get_chat_sessions(
    user_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if user_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Cannot view another user's sessions.", "keys": []},
        )
    service = HistoryService(db)
    sessions = service.get_user_sessions(user_id)
    if not sessions:
        raise HTTPException(
            status_code=404, detail="No chat sessions found for this user"
        )
    return sessions


@router.get("/chat_history/{session_id}", response_model=list[ChatMessageSchema])
def get_chat_history(
    session_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = HistoryService(db)
    messages = service.get_session_messages(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this session")
    if user.role != "admin" and any(m.user_id != user.id for m in messages):
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Cannot view another user's chat.", "keys": []},
        )
    return messages
