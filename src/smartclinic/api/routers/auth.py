from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_db, get_mailer_service
from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.auth.auth_controller import (
    login_user_controller,
    register_user_controller,
)
from smartclinic.core.auth.auth_dto import LoginDTO, RegisterUserDTO
from smartclinic.core.mailer.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(
    user: RegisterUserDTO,
    db: Annotated[Session, Depends(get_db)],
    mailer: Annotated[EmailService, Depends(get_mailer_service)],
):
    return register_user_controller(mailer, user, db)


@router.post("/login")
def login(
    login_data: LoginDTO,
    db: Annotated[Session, Depends(get_db)],
):
    return login_user_controller(login_data, db)


@router.get("/me")
def me(user: Annotated[CurrentUser, Depends(get_current_user)]):
    return {
        "user_id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "role": user.role,
    }
