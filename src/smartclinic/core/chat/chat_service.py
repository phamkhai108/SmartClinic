import re
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
from smartclinic.core.search.search_service import search_vector_cosine


def context_rag(client: Elasticsearch, query: str, embedding_model: LLMModel) -> str:
    list_chunks = search_vector_cosine(client, embedding_model, query, size=4)

    combined_content = ""

    for chunk in list_chunks.hits:
        combined_content += chunk.chunk_content + " . "

    return combined_content.strip()


chat_histories: dict[str, list[choiceMessage]] = {}


def process_chat(
    chat_dto: ChatMessageDto,
    llm_model: LLMModel,
    embedding_model: LLMModel,
    client: Elasticsearch,
) -> ChatResponseDto:
    user_id = chat_dto.user_id
    session_id = chat_dto.session_id
    user_messages = chat_dto.messages

    context = context_rag(
        client=client,
        query=user_messages[-1].content,
        embedding_model=embedding_model,
    )

    session_history = chat_histories.get(session_id, [])

    context_messages: list[dict] = []

    context_messages.append(
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    )

    for past_choice in session_history:
        for msg in past_choice.messages:
            context_messages.append({"role": msg.role, "content": msg.content})

    context_messages.extend({"role": m.role, "content": m.content} for m in user_messages)

    # print("Final context_messages for LLM:")
    # pprint.pprint(context_messages)

    bot_content = llm_model.chat(context_messages)

    bot_content = clean_think_block(bot_content)  # clean think block

    bot_reply = Message(role="assistant", content=bot_content)

    new_choice = choiceMessage(
        messages=user_messages + [bot_reply],
        message_id=str(uuid.uuid4()),
        time_at=datetime.now(),
        finish_reason="stop",
    )

    chat_histories.setdefault(session_id, []).append(new_choice)

    return ChatResponseDto(
        user_id=user_id,
        choice=new_choice,
        history=chat_histories[session_id],
        reference=["ref-doc-1", "ref-doc-2"],
        time_at=datetime.now(),
    )


def clean_think_block(text: str) -> str:
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return cleaned_text
