from datetime import datetime

import bcrypt
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
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

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="files")


# Khởi tạo database (ví dụ sqlite)
if __name__ == "__main__":
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
