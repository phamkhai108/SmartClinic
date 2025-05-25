from sqlalchemy.orm import Session

from smartclinic.core.user.user_dto import UserDTO
from smartclinic.sql.setup_db import User


def get_all_users(db: Session):
    users = db.query(User).all()
    return [
        UserDTO(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            role=user.role,
        )
        for user in users
    ]


def update_user_role(user_id: str, new_role: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    if new_role not in ("user", "doctor"):
        raise ValueError("Invalid role")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user
