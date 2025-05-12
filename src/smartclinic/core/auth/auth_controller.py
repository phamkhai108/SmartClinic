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


def register_user_controller(mailer: EmailService, user: RegisterUserDTO, db: Session):
    existing_user = db.query(setup_db.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    if not user.code_verify:
        code = send_verification_code(mailer, user.email)
        if not code:
            raise HTTPException(
                status_code=500, detail="Failed to send verification email."
            )
        return {"message": "Verification code sent to your email."}

    is_valid, error = validate_code(user.email, user.code_verify)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    new_user = setup_db.User(user_name=user.user_name, email=user.email, role="user")
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()

    remove_code(user.email)

    return {"message": "User registered successfully."}


def login_user_controller(login: LoginDTO, db: Session):
    user = db.query(setup_db.User).filter_by(email=login.email).first()
    if not user or not authenticate_user(user, login.password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    access_token = create_access_token(
        data={
            "user_id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "role": user.role,
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}
