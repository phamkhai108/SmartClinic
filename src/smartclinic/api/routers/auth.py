from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_db, get_mailer_service
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
    db: Session = Depends(get_db),  # noqa: B008
    mailer: EmailService = Depends(get_mailer_service),  # noqa: B008
):  # noqa: B008
    return register_user_controller(mailer, user, db)


@router.post("/login")
def login(
    login_data: LoginDTO,
    db: Session = Depends(get_db),  # noqa: B008
):
    return login_user_controller(login_data, db)
