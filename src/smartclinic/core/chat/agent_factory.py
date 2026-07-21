from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from smartclinic.common.base import Settings
from smartclinic.core.chat.chat_contants import SYSTEM_PROMPT, SYSTEM_PROMPT_NO_SEARCH
from smartclinic.core.chat.tools.search_documents import (
    SearchRunContext,
    build_search_documents_tool,
)
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.vectordb.protocols import ChunkRepository


def build_chat_model(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=settings.openai_api_url,
        api_key=settings.openai_api_key or "unused",
        model=settings.model_llm_id,
        temperature=0.2,
        streaming=True,
        timeout=60,
    )


def build_chat_agent(
    settings: Settings,
    run_context: SearchRunContext,
    repository: ChunkRepository | None = None,
    embedding_model: LLMModel | None = None,
) -> Any:
    model = build_chat_model(settings)
    tools: list[Any] = []
    system_prompt = SYSTEM_PROMPT_NO_SEARCH

    if repository is not None and embedding_model is not None:
        tools = [
            build_search_documents_tool(
                repository=repository,
                embedding_model=embedding_model,
                run_context=run_context,
            )
        ]
        system_prompt = SYSTEM_PROMPT

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        name="smartclinic-chat-agent",
    )
