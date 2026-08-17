from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_db
from smartclinic.common.base import get_settings
from smartclinic.sql.setup_db import User

security = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, id: str, user_name: str, email: str, role: str):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.role = role


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Missing bearer token.",
                "keys": [],
            },
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            get_settings().jwt_secret,
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid or expired token.",
                "keys": [],
            },
        ) from exc

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Invalid token payload.",
                "keys": [],
            },
        )

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "User not found.", "keys": []},
        )

    return CurrentUser(
        id=str(user.id),
        user_name=user.user_name,
        email=user.email,
        role=user.role,
    )


def require_roles(*roles: str):
    allowed = set(roles)

    def checker(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Role '{user.role}' is not allowed.",
                    "keys": [],
                },
            )
        return user

    return checker
