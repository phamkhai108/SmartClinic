from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from smartclinic.core.chat_history.chat_history_dto import SessionInfo
from smartclinic.sql.setup_db import ChatHistory


class HistoryService:
    def __init__(self, session: Session):
        self.session = session

    def insert_by_session(
        self,
        session_id: str,
        user_id: str,
        conversation_name: str,
        message: Any,
        sender: str,
        timestamp=None,
    ) -> ChatHistory:
        """Thêm một bản ghi chat mới."""
        chat = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            conversation_name=conversation_name,
            message=message,
            sender=sender,
            timestamp=timestamp or datetime.now(UTC),
        )
        self.session.add(chat)
        self.session.commit()
        return chat

    def update_chat_by_session(
        self,
        session_id: str,
        new_message: Any = None,
        new_conversation_name: Any = None,
    ) -> None:
        """Cập nhật message và/hoặc conversation_name theo session_id."""
        chats = (
            self.session.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .all()
        )
        if not chats:
            print(f"No chats found for session_id={session_id}")
            return

        for chat in chats:
            if new_message:
                chat.message = new_message
            if new_conversation_name:
                chat.conversation_name = new_conversation_name

        self.session.commit()
        print(f"Updated {len(chats)} chat(s) for session_id={session_id}")

    def delete_chat_by_session(self, session_id: str) -> None:
        """Xóa tất cả chat theo session_id."""
        deleted_count = (
            self.session.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .delete()
        )
        self.session.commit()
        print(f"Deleted {deleted_count} chat(s) for session_id={session_id}")

    def get_session_messages(self, session_id: str) -> list[ChatHistory]:
        return (
            self.session.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.timestamp.asc())
            .all()
        )

    def get_user_sessions(self, user_id: str) -> list[SessionInfo]:
        from sqlalchemy import func

        subq = (
            self.session.query(
                ChatHistory.session_id,
                func.max(ChatHistory.timestamp).label("latest_timestamp"),
            )
            .filter(ChatHistory.user_id == user_id)
            .group_by(ChatHistory.session_id)
            .subquery()
        )

        rows = (
            self.session.query(
                ChatHistory.session_id,
                ChatHistory.conversation_name,
                subq.c.latest_timestamp,
            )
            .join(
                subq,
                (ChatHistory.session_id == subq.c.session_id)
                & (ChatHistory.timestamp == subq.c.latest_timestamp),
            )
            .order_by(subq.c.latest_timestamp.desc())
            .all()
        )

        return [
            SessionInfo(
                session_id=row.session_id,
                conversation_name=row.conversation_name,
                latest_timestamp=row.latest_timestamp,
            )
            for row in rows
        ]
