# app/service.py

import random
import uuid
from datetime import datetime

from smartclinic.core.chat.chat_dto import (
    ChatMessageDto,
    ChatResponseDto,
    Message,
    choiceMessage,
)

chat_histories: dict[str, list[choiceMessage]] = {}

# data sample chat
fake_responses = [
    "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?",
    "Bạn vui lòng nói rõ hơn được không?",
    "Đây là một câu hỏi thú vị!",
    "Tôi cần thêm thông tin để trả lời chính xác.",
    "Cảm ơn bạn đã hỏi!"
]


def get_bot_reply() -> str:
    return random.choice(fake_responses)


def process_chat(chat_dto: ChatMessageDto) -> ChatResponseDto:
    user_id = chat_dto.user_id
    user_messages = chat_dto.messages

    bot_reply = Message(role="assistant", content=get_bot_reply())

    new_choice = choiceMessage(
        messages=user_messages + [bot_reply],
        message_id=str(uuid.uuid4()),
        time_at=datetime.now(),
        finish_reason="stop"
    )

    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append(new_choice)

    return ChatResponseDto(
        user_id=user_id,
        choice=new_choice,
        history=chat_histories[user_id],
        reference=["ref-doc-1", "ref-doc-2"],
        time_at=datetime.now()
    )


