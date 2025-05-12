from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from smartclinic.core.mailer import EmailService
from smartclinic.core.mailer.email_controller import handel_mail

# In-memory cache lưu mã xác minh
verify_codes = {}


def send_verification_code(mailer: EmailService, email: str) -> str | None:
    response = handel_mail(mailer, email)
    if not response.code_verify:
        return None

    verify_codes[email] = {
        "code": response.code_verify,
        "expires": datetime.now(UTC) + timedelta(minutes=5),
    }
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


# Secret này nên đưa vào env
SECRET_KEY = "your_jwt_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def authenticate_user(user, password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
