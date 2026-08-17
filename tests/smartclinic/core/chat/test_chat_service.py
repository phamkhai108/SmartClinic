from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from smartclinic.api.deps_auth import CurrentUser
from smartclinic.common.base import get_settings
from smartclinic.core.chat.chat_dto import ChatMessageDto, Message
from smartclinic.core.chat.chat_service import (
    _chunk_text,
    _history_from_db,
    _persist_turn,
    _to_langchain_messages,
    clean_think_block,
    ensure_llm_config,
    format_sse,
    resolve_optional_search_deps,
    stream_agent_chat,
)


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_URL", "http://llm.test")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_KEY", "key")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "model")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_ensure_llm_config_raises_when_missing(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_LLM_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        ensure_llm_config()
    assert exc.value.status_code == 503
    assert "SMARTCLINIC_LLM_API_URL" in exc.value.detail["keys"]


def test_resolve_optional_search_deps_skips_without_es(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_VECTOR_BACKEND", "elasticsearch")
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "")
    get_settings.cache_clear()
    assert resolve_optional_search_deps() == (None, None)


def test_resolve_optional_search_deps_skips_without_embed(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_VECTOR_BACKEND", "elasticsearch")
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "http://es")
    monkeypatch.setenv("SMARTCLINIC_EMBED_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_MODEL_EMBED_ID", "")
    get_settings.cache_clear()
    assert resolve_optional_search_deps() == (None, None)


def test_resolve_optional_search_deps_swallows_factory_errors(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_VECTOR_BACKEND", "elasticsearch")
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "http://es")
    monkeypatch.setenv("SMARTCLINIC_EMBED_API_URL", "http://embed")
    monkeypatch.setenv("SMARTCLINIC_EMBED_API_KEY", "k")
    monkeypatch.setenv("SMARTCLINIC_MODEL_EMBED_ID", "emb")
    get_settings.cache_clear()

    def boom(_settings):
        raise RuntimeError("down")

    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.build_chunk_repository",
        boom,
    )
    assert resolve_optional_search_deps() == (None, None)


def test_clean_think_block_strips_reasoning():
    text = "hello <think>secret</think> world"
    assert clean_think_block(text) == "hello  world"


def test_chunk_text_ignores_non_ai_and_tool_calls():
    assert _chunk_text("plain") == ""
    tool_chunk = AIMessageChunk(content="", tool_call_chunks=[{"index": 0}])
    assert _chunk_text(tool_chunk) == ""


def test_chunk_text_handles_str_and_list_content():
    assert _chunk_text(AIMessageChunk(content="hi")) == "hi"
    chunk = AIMessageChunk(
        content=["a", {"type": "text", "text": "b"}, {"type": "other"}]
    )
    assert _chunk_text(chunk) == "ab"


def test_history_and_langchain_mapping():
    history_service = MagicMock()
    history_service.get_session_messages.return_value = [
        SimpleNamespace(sender="user", message="q"),
        SimpleNamespace(sender="assistant", message="a"),
    ]
    msgs = _history_from_db(history_service, "s1")
    assert msgs == [
        Message(role="user", content="q"),
        Message(role="assistant", content="a"),
    ]
    lc = _to_langchain_messages(msgs, [Message(role="user", content="next")])
    assert isinstance(lc[0], HumanMessage)
    assert isinstance(lc[1], AIMessage)
    assert isinstance(lc[2], HumanMessage)


def test_persist_turn_uses_existing_conversation_name():
    history_service = MagicMock()
    history_service.get_session_messages.return_value = [
        SimpleNamespace(conversation_name="Old title", message="x", sender="user")
    ]
    payload = ChatMessageDto(
        user_id="u1",
        session_id="s1",
        messages=[Message(role="user", content="new")],
    )
    choice = _persist_turn(payload, "bot", history_service)
    assert choice.finish_reason == "stop"
    assert choice.messages[-1].content == "bot"
    assert history_service.insert_by_session.call_count == 2
    first_call = history_service.insert_by_session.call_args_list[0].kwargs
    assert first_call["conversation_name"] == "Old title"


def test_persist_turn_names_from_first_user_message():
    history_service = MagicMock()
    history_service.get_session_messages.return_value = []
    payload = ChatMessageDto(
        user_id="u1",
        session_id="s1",
        messages=[Message(role="user", content="First question")],
    )
    _persist_turn(payload, "bot", history_service)
    first_call = history_service.insert_by_session.call_args_list[0].kwargs
    assert first_call["conversation_name"] == "First question"


def test_format_sse_prefix_and_json():
    raw = format_sse({"type": "token", "content": "xin chào"})
    assert raw.startswith("data: ")
    assert raw.endswith("\n\n")
    payload = json.loads(raw.removeprefix("data: ").strip())
    assert payload["content"] == "xin chào"


def test_stream_agent_chat_emits_tokens_references_and_done(monkeypatch):
    async def fake_astream(_state, stream_mode="messages"):
        yield AIMessageChunk(content="Xin")
        yield AIMessageChunk(content=" chào")

    agent = MagicMock()
    agent.astream = fake_astream

    def fake_build(**kwargs):
        kwargs["run_context"].sources.append("doc.pdf")
        return agent

    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.resolve_optional_search_deps",
        lambda: (None, None),
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.build_chat_agent",
        fake_build,
    )

    history_service = MagicMock()
    history_service.get_session_messages.return_value = []
    payload = ChatMessageDto(
        user_id="u1",
        session_id="s1",
        messages=[Message(role="user", content="hi")],
    )

    async def collect():
        return [event async for event in stream_agent_chat(payload, history_service)]

    events = asyncio.run(collect())
    types = [e["type"] for e in events]
    assert types.count("token") == 2
    assert "references" in types
    assert types[-1] == "done"
    assert events[-1]["content"] == "Xin chào"
    assert history_service.insert_by_session.call_count == 2


def test_stream_agent_chat_yields_error_on_agent_failure(monkeypatch):
    async def failing_astream(_state, stream_mode="messages"):
        raise RuntimeError("boom")
        yield  # pragma: no cover

    agent = MagicMock()
    agent.astream = failing_astream
    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.resolve_optional_search_deps",
        lambda: (None, None),
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.build_chat_agent",
        lambda **_k: agent,
    )
    history_service = MagicMock()
    history_service.get_session_messages.return_value = []
    payload = ChatMessageDto(
        user_id="u1",
        session_id="s1",
        messages=[Message(role="user", content="hi")],
    )

    async def collect():
        return [event async for event in stream_agent_chat(payload, history_service)]

    events = asyncio.run(collect())
    assert events == [
        {"type": "error", "code": "AGENT_ERROR", "message": "boom"},
    ]
    history_service.insert_by_session.assert_not_called()


def test_stream_agent_chat_fallback_on_empty_reply(monkeypatch):
    async def empty_astream(_state, stream_mode="messages"):
        yield AIMessageChunk(content="")

    agent = MagicMock()
    agent.astream = empty_astream
    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.resolve_optional_search_deps",
        lambda: (None, None),
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.chat_service.build_chat_agent",
        lambda **_k: agent,
    )
    history_service = MagicMock()
    history_service.get_session_messages.return_value = []
    payload = ChatMessageDto(
        user_id="u1",
        session_id="s1",
        messages=[Message(role="user", content="hi")],
    )

    async def collect():
        return [event async for event in stream_agent_chat(payload, history_service)]

    events = asyncio.run(collect())
    done = events[-1]
    assert done["type"] == "done"
    assert "Xin lỗi" in done["content"]


def test_chat_endpoint_forbids_other_user():
    from smartclinic.api.routers.chat import chat_endpoint

    payload = ChatMessageDto(
        user_id="other",
        session_id="s1",
        messages=[Message(role="user", content="hi")],
    )
    user = CurrentUser(id="u1", user_name="a", email="a@b.com", role="user")

    async def run():
        with pytest.raises(HTTPException) as exc:
            await chat_endpoint(payload, user)
        return exc.value

    err = asyncio.run(run())
    assert err.status_code == 403
    assert err.detail["code"] == "FORBIDDEN"


def test_chat_endpoint_allows_admin_impersonation(monkeypatch):
    from smartclinic.api.routers.chat import chat_endpoint

    monkeypatch.setattr(
        "smartclinic.api.routers.chat.ensure_llm_config",
        lambda: None,
    )
    payload = ChatMessageDto(
        user_id="other",
        session_id="s1",
        messages=[Message(role="user", content="hi")],
    )
    user = CurrentUser(id="admin1", user_name="admin", email="a@b.com", role="admin")

    async def run():
        return await chat_endpoint(payload, user)

    response = asyncio.run(run())
    assert response.media_type == "text/event-stream"
