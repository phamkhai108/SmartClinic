from __future__ import annotations

import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from smartclinic.core.auth.auth_dto import LoginDTO, RegisterUserDTO
from smartclinic.core.auth.auth_service import (
    authenticate_user,
    create_access_token,
    remove_code,
    send_verification_code,
    validate_code,
)
from smartclinic.core.mailer.email_service import EmailService
from smartclinic.sql import setup_db

logger = logging.getLogger(__name__)


def register_user_controller(mailer: EmailService, user: RegisterUserDTO, db: Session):
    existing_user = db.query(setup_db.User).filter_by(email=user.email).first()
    if existing_user:
        logger.info("Register rejected: email already registered (%s)", user.email)
        raise HTTPException(status_code=400, detail="Email already registered.")

    if not user.code_verify:
        code = send_verification_code(mailer, user.email)
        if not code:
            logger.error("Failed to send verification email to %s", user.email)
            raise HTTPException(
                status_code=500, detail="Failed to send verification email."
            )
        return {"message": "Verification code sent to your email."}

    is_valid, error = validate_code(user.email, user.code_verify)
    if not is_valid:
        logger.info("Register OTP invalid for %s: %s", user.email, error)
        raise HTTPException(status_code=400, detail=error)

    new_user = setup_db.User(user_name=user.user_name, email=user.email, role="user")
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()

    remove_code(user.email)
    logger.info("User registered successfully: %s (%s)", user.email, new_user.id)

    return {"message": "User registered successfully."}


def login_user_controller(login: LoginDTO, db: Session):
    user = db.query(setup_db.User).filter_by(email=login.email).first()
    if not user or not authenticate_user(user, login.password):
        logger.warning("Login failed for email=%s", login.email)
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    access_token = create_access_token(
        data={
            "user_id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "role": user.role,
        }
    )
    logger.info("Login success email=%s role=%s", user.email, user.role)

    return {"access_token": access_token, "token_type": "bearer"}
