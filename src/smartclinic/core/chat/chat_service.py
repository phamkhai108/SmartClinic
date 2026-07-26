from __future__ import annotations

import json
import logging
import re
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from smartclinic.common.base import get_settings
from smartclinic.common.errors import missing_config_error
from smartclinic.core.chat.agent_factory import build_chat_agent
from smartclinic.core.chat.chat_dto import (
    ChatMessageDto,
    Message,
    choiceMessage,
)
from smartclinic.core.chat_history.chat_history_service import HistoryService
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.vectordb.factory import build_chunk_repository
from smartclinic.vectordb.protocols import ChunkRepository

logger = logging.getLogger(__name__)

chat_histories: dict[str, list[choiceMessage]] = {}


class AgentRunContext:
    def __init__(self) -> None:
        self.sources: list[str] = []


def ensure_llm_config() -> None:
    settings = get_settings()
    missing: list[str] = []
    if not settings.resolved_llm_api_url:
        missing.append("SMARTCLINIC_LLM_API_URL")
    if not settings.model_llm_id:
        missing.append("SMARTCLINIC_MODEL_LLM_ID")
    if missing:
        raise missing_config_error(missing)


def resolve_optional_search_deps() -> tuple[ChunkRepository | None, LLMModel | None]:
    settings = get_settings()
    if settings.vector_backend == "elasticsearch" and not settings.es_host:
        return None, None
    if settings.vector_backend == "milvus" and not settings.milvus_uri:
        return None, None
    if not settings.resolved_embed_api_url or not settings.model_embed_id:
        logger.info("Document search disabled: embedding config incomplete.")
        return None, None

    try:
        repository = build_chunk_repository(settings)
        embedding_model = LLMModel(
            openai_api_url=settings.resolved_embed_api_url,
            openai_api_key=settings.resolved_embed_api_key,
            model_id=settings.model_embed_id,
        )
        return repository, embedding_model
    except Exception as exc:
        logger.warning("Document search disabled: %s", exc)
        return None, None


def _to_langchain_messages(
    session_history: list[choiceMessage],
    user_messages: list[Message],
) -> list[Any]:
    messages: list[Any] = []
    for past in session_history:
        for msg in past.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
    for msg in user_messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    return messages


def clean_think_block(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _chunk_text(chunk: Any) -> str:
    if not isinstance(chunk, AIMessageChunk):
        return ""
    if getattr(chunk, "tool_call_chunks", None):
        return ""
    content = chunk.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return ""


def _persist_turn(
    payload: ChatMessageDto,
    bot_content: str,
    history_service: HistoryService,
) -> choiceMessage:
    user_id = payload.user_id
    session_id = payload.session_id
    user_messages = payload.messages

    existing = history_service.get_session_messages(session_id)
    conversation_name = (
        existing[0].conversation_name if existing else user_messages[0].content
    )

    for msg in user_messages:
        history_service.insert_by_session(
            session_id=session_id,
            user_id=user_id,
            conversation_name=conversation_name,
            message=msg.content,
            sender=msg.role,
            timestamp=datetime.now(),
        )

    bot_reply = Message(role="assistant", content=bot_content)
    history_service.insert_by_session(
        session_id=session_id,
        user_id=user_id,
        conversation_name=conversation_name,
        message=bot_reply.content,
        sender="assistant",
        timestamp=datetime.now(),
    )

    new_choice = choiceMessage(
        messages=[*list(user_messages), bot_reply],
        message_id=str(uuid.uuid4()),
        time_at=datetime.now(),
        finish_reason="stop",
    )
    chat_histories.setdefault(session_id, []).append(new_choice)
    return new_choice


async def stream_agent_chat(
    payload: ChatMessageDto,
    history_service: HistoryService,
) -> AsyncIterator[dict[str, Any]]:
    settings = get_settings()
    run_context = AgentRunContext()
    repository, embedding_model = resolve_optional_search_deps()
    rag_enabled = repository is not None and embedding_model is not None

    user_preview = ""
    if payload.messages:
        user_preview = (payload.messages[-1].content or "")[:120]

    logger.info(
        "chat.start session=%s user=%s rag=%s llm=%s preview=%r",
        payload.session_id,
        payload.user_id,
        rag_enabled,
        settings.model_llm_id,
        user_preview,
    )

    agent = build_chat_agent(
        settings=settings,
        run_context=run_context,
        repository=repository,
        embedding_model=embedding_model,
    )

    session_history = chat_histories.get(payload.session_id, [])
    lc_messages = _to_langchain_messages(session_history, payload.messages)

    assembled: list[str] = []
    refs_sent = False
    token_events = 0

    try:
        async for item in agent.astream(
            {"messages": lc_messages},
            stream_mode="messages",
        ):
            message_chunk = item[0] if isinstance(item, tuple) else item
            text = _chunk_text(message_chunk)
            if text:
                assembled.append(text)
                token_events += 1
                yield {"type": "token", "content": text}

            if run_context.sources and not refs_sent:
                refs_sent = True
                logger.info(
                    "chat.references session=%s sources=%s",
                    payload.session_id,
                    run_context.sources,
                )
                yield {"type": "references", "references": list(run_context.sources)}

    except Exception as exc:
        logger.exception(
            "chat.error session=%s user=%s: %s",
            payload.session_id,
            payload.user_id,
            exc,
        )
        yield {
            "type": "error",
            "code": "AGENT_ERROR",
            "message": str(exc),
        }
        return

    if run_context.sources and not refs_sent:
        logger.info(
            "chat.references session=%s sources=%s",
            payload.session_id,
            run_context.sources,
        )
        yield {"type": "references", "references": list(run_context.sources)}

    raw = "".join(assembled)
    bot_content = clean_think_block(raw) or raw
    if not bot_content.strip():
        logger.warning(
            "chat.empty_reply session=%s tokens=%s — using fallback message",
            payload.session_id,
            token_events,
        )
        bot_content = "Xin lỗi, tôi chưa tạo được phản hồi. Vui lòng thử lại."

    choice = _persist_turn(payload, bot_content, history_service)
    logger.info(
        "chat.done session=%s message_id=%s tokens=%s chars=%s sources=%s",
        payload.session_id,
        choice.message_id,
        token_events,
        len(bot_content),
        run_context.sources or [],
    )
    yield {
        "type": "done",
        "message_id": choice.message_id,
        "session_id": payload.session_id,
        "content": bot_content,
    }


def format_sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
