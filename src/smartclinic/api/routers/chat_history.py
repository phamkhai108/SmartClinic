from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_database_client
from smartclinic.core.chat_history.chat_history_dto import ChatMessageSchema, SessionInfo
from smartclinic.core.chat_history.chat_history_service import HistoryService

router = APIRouter(prefix="/chat_history", tags=["Chat history"])


@router.get("/chat_sessions/{user_id}", response_model=list[SessionInfo])
def get_chat_sessions(user_id: str, db: Session = Depends(get_database_client)):
    service = HistoryService(db)
    sessions = service.get_user_sessions(user_id)
    if not sessions:
        raise HTTPException(
            status_code=404, detail="No chat sessions found for this user"
        )
    return sessions


@router.get("/chat_history/{session_id}", response_model=list[ChatMessageSchema])
def get_chat_history(session_id: str, db: Session = Depends(get_database_client)):
    service = HistoryService(db)
    messages = service.get_session_messages(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this session")
    return messages
