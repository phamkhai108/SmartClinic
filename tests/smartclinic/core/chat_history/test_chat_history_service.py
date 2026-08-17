from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smartclinic.core.chat_history.chat_history_service import HistoryService
from smartclinic.sql.setup_db import Base, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User(id="u1", user_name="alice", email="a@b.com", role="user")
    user.set_password("secret")
    session.add(user)
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_insert_and_get_session_messages_ordered(db_session):
    svc = HistoryService(db_session)
    t0 = datetime.now(UTC)
    svc.insert_by_session("s1", "u1", "Chat", "first", "user", t0)
    svc.insert_by_session(
        "s1",
        "u1",
        "Chat",
        "second",
        "assistant",
        t0 + timedelta(seconds=1),
    )
    rows = svc.get_session_messages("s1")
    assert [r.message for r in rows] == ["first", "second"]


def test_update_chat_by_session_renames(db_session):
    svc = HistoryService(db_session)
    svc.insert_by_session("s1", "u1", "Old", "hi", "user")
    svc.update_chat_by_session("s1", new_conversation_name="New")
    rows = svc.get_session_messages("s1")
    assert rows[0].conversation_name == "New"


def test_update_chat_by_session_noop_when_missing(db_session):
    svc = HistoryService(db_session)
    svc.update_chat_by_session("missing", new_conversation_name="X")
    assert svc.get_session_messages("missing") == []


def test_delete_chat_by_session(db_session):
    svc = HistoryService(db_session)
    svc.insert_by_session("s1", "u1", "Chat", "hi", "user")
    svc.delete_chat_by_session("s1")
    assert svc.get_session_messages("s1") == []


def test_get_user_sessions_latest_desc(db_session):
    svc = HistoryService(db_session)
    t0 = datetime.now(UTC)
    svc.insert_by_session("s1", "u1", "A", "a", "user", t0)
    svc.insert_by_session(
        "s2",
        "u1",
        "B",
        "b",
        "user",
        t0 + timedelta(seconds=5),
    )
    sessions = svc.get_user_sessions("u1")
    assert [s.session_id for s in sessions] == ["s2", "s1"]
    assert sessions[0].conversation_name == "B"
