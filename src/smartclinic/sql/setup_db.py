import uuid
from datetime import UTC, datetime

import bcrypt
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_name = Column(String(50), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(50), nullable=False)

    files = relationship("File", back_populates="user")

    def set_password(self, raw_password):
        hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        self.password = hashed.decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password.encode("utf-8"))


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="files")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    conversation_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    sender = Column(Enum("user", "assistant", name="sender_type"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", backref="chat_history")


# Khởi tạo database (ví dụ sqlite)
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///example.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    new_user = User(user_name="test_user", email="test@example.com", role="admin")
    new_user.set_password("securepassword123")
    session.add(new_user)
    session.commit()

    print(f"User {new_user.user_name} created with ID {new_user.id}")

    file1 = File(
        id="file1",
        user_id=new_user.id,
        file_name="photo.jpg",
        status="pending",
        created_at=datetime(2024, 12, 1, 12, 0, 0),
    )
    file2 = File(
        id="file2",
        user_id=new_user.id,
        file_name="report.docx",
        status="active",
        created_at=datetime(2023, 10, 1, 12, 0, 0),
    )

    session.add_all([file1, file2])
    session.commit()

    print("Multiple files added successfully.")

    # --- DỮ LIỆU ẢO CHO CHAT HISTORY ---
    from uuid import uuid4

    session_id = str(uuid4())  # Một session giả

    chat1 = ChatHistory(
        session_id=session_id,
        user_id=new_user.id,
        conversation_name="Cuộc trò chuyện 1",  # Conversation name
        message="Xin chào!",
        sender="user",
        timestamp=datetime.utcnow(),
    )

    chat2 = ChatHistory(
        session_id=session_id,
        user_id=new_user.id,
        conversation_name="Cuộc trò chuyện 1",  # Conversation name
        message="Chào bạn, tôi có thể giúp gì?",
        sender="assistant",
        timestamp=datetime.now(UTC),
    )

    chat3 = ChatHistory(
        session_id=session_id,
        user_id=new_user.id,
        conversation_name="Cuộc trò chuyện 1",  # Conversation name
        message="Tôi cần xem lại tập tin hôm trước.",
        sender="user",
        timestamp=datetime.now(UTC),
    )

    # Thêm vào session và commit
    session.add_all([chat1, chat2, chat3])
    session.commit()

    print("Sample chat history with conversation_name inserted.")
