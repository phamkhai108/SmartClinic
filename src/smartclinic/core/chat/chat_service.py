import uuid
from datetime import datetime

from elasticsearch import Elasticsearch

from smartclinic.core.chat.chat_contants import SYSTEM_PROMPT
from smartclinic.core.chat.chat_dto import (
    ChatMessageDto,
    ChatResponseDto,
    Message,
    choiceMessage,
)
from smartclinic.core.llm.llm_service import LLMModel
from smartclinic.core.search.search_service import search_fulltext

chat_histories: dict[str, list[choiceMessage]] = {}


def context_rag(client: Elasticsearch, query: str) -> str:
    list_chunks = search_fulltext(client, query, size=3)

    combined_content = ""

    for chunk in list_chunks.hits:
        combined_content += chunk.chunk_content + " . "

    return combined_content.strip()


def process_chat(
    chat_dto: ChatMessageDto,
    embedding_model: LLMModel,
    client: Elasticsearch,
) -> ChatResponseDto:
    user_id = chat_dto.user_id
    user_messages = chat_dto.messages

    context = context_rag(
        client=client,
        query=user_messages[-1].content,
    )

    context_messages: list[dict] = []
    if user_id in chat_histories:
        for past_choice in chat_histories[user_id]:
            for msg in past_choice.messages:
                context_messages.append({"role": msg.role, "content": msg.content})

    current_messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    ]
    current_messages.extend({"role": m.role, "content": m.content} for m in user_messages)

    context_messages += current_messages

    bot_content = embedding_model.chat(context_messages)

    bot_reply = Message(role="assistant", content=bot_content)

    new_choice = choiceMessage(
        messages=user_messages + [bot_reply],
        message_id=str(uuid.uuid4()),
        time_at=datetime.now(),
        finish_reason="stop",
    )

    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append(new_choice)

    return ChatResponseDto(
        user_id=user_id,
        choice=new_choice,
        history=chat_histories[user_id],
        reference=["ref-doc-1", "ref-doc-2"],
        time_at=datetime.now(),
    )
