from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from smartclinic.common.base import get_settings
from smartclinic.core.mailer import EmailService
from smartclinic.core.mailer.email_controller import handle_mail

logger = logging.getLogger(__name__)

verify_codes: dict[str, dict] = {}
ALGORITHM = "HS256"


def send_verification_code(mailer: EmailService, email: str) -> str | None:
    response = handle_mail(mailer, email)
    if not response.code_verify:
        logger.warning("Verification email failed for %s", email)
        return None

    verify_codes[email] = {
        "code": response.code_verify,
        "expires": datetime.now(UTC) + timedelta(minutes=5),
    }
    logger.info("Verification code issued for %s (expires in 5m)", email)
    return response.code_verify


def validate_code(email: str, code: str):
    data = verify_codes.get(email)
    if not data:
        return False, "No verification code sent."
    if data["expires"] < datetime.now(UTC):
        return False, "Verification code expired."
    if data["code"] != code:
        return False, "Invalid verification code."
    return True, None


def remove_code(email: str):
    verify_codes.pop(email, None)


def authenticate_user(user, password: str) -> bool:
    check = getattr(user, "check_password", None)
    if callable(check):
        return check(password)
    return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
