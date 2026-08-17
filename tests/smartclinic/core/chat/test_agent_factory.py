from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from smartclinic.common.base import get_settings
from smartclinic.core.chat.agent_factory import build_chat_agent
from smartclinic.core.chat.chat_constants import SYSTEM_PROMPT, SYSTEM_PROMPT_NO_SEARCH


def test_build_chat_agent_without_search(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_URL", "http://llm.test")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_KEY", "key")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "model")
    get_settings.cache_clear()

    captured: dict = {}

    monkeypatch.setattr(
        "smartclinic.core.chat.agent_factory.build_chat_model",
        lambda _s: MagicMock(name="model"),
    )

    def fake_create_agent(**kwargs):
        captured.update(kwargs)
        return MagicMock(name="agent")

    monkeypatch.setattr(
        "smartclinic.core.chat.agent_factory.create_agent",
        fake_create_agent,
    )

    agent = build_chat_agent(
        settings=get_settings(),
        run_context=SimpleNamespace(sources=[]),
        repository=None,
        embedding_model=None,
    )
    assert agent is not None
    assert captured["tools"] == []
    assert captured["system_prompt"] == SYSTEM_PROMPT_NO_SEARCH
    get_settings.cache_clear()


def test_build_chat_agent_with_search_attaches_tool(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_URL", "http://llm.test")
    monkeypatch.setenv("SMARTCLINIC_LLM_API_KEY", "key")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "model")
    get_settings.cache_clear()

    captured: dict = {}
    tool = MagicMock(name="search_tool")

    monkeypatch.setattr(
        "smartclinic.core.chat.agent_factory.build_chat_model",
        lambda _s: MagicMock(name="model"),
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.agent_factory.build_search_documents_tool",
        lambda **_k: tool,
    )
    monkeypatch.setattr(
        "smartclinic.core.chat.agent_factory.create_agent",
        lambda **kwargs: captured.update(kwargs) or MagicMock(name="agent"),
    )

    build_chat_agent(
        settings=get_settings(),
        run_context=SimpleNamespace(sources=[]),
        repository=MagicMock(),
        embedding_model=MagicMock(),
    )
    assert captured["tools"] == [tool]
    assert captured["system_prompt"] == SYSTEM_PROMPT
    get_settings.cache_clear()
