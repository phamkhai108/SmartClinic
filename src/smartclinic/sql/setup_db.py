from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

import bcrypt
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from smartclinic.common.base import get_settings

logger = logging.getLogger("smartclinic")
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


def setup_db():
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {},
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        if session.query(User).count() == 0:
            admin = User(user_name="admin", email="admin@example.com", role="admin")
            admin.set_password("admin")
            doctor = User(user_name="doctor", email="doctor@gmail.com", role="doctor")
            doctor.set_password("doctor")
            session.add_all([admin, doctor])
            session.commit()
            logger.info("Seeded default admin/doctor users.")
    finally:
        session.close()

    return engine


if __name__ == "__main__":
    setup_db()
