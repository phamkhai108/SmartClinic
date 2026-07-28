from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import bcrypt
import jwt
import pytest

from smartclinic.common.base import get_settings
from smartclinic.core.auth import auth_service
from smartclinic.core.mailer.email_dto import EmailResponseDTO


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    auth_service.verify_codes.clear()


def test_validate_code_accepts_matching_code():
    auth_service.verify_codes["a@b.com"] = {
        "code": "123456",
        "expires": datetime.now(UTC) + timedelta(minutes=5),
    }
    ok, err = auth_service.validate_code("a@b.com", "123456")
    assert ok is True
    assert err is None


def test_validate_code_rejects_missing_code():
    ok, err = auth_service.validate_code("nobody@b.com", "123456")
    assert ok is False
    assert "No verification code" in err


def test_validate_code_rejects_expired():
    auth_service.verify_codes["a@b.com"] = {
        "code": "123456",
        "expires": datetime.now(UTC) - timedelta(seconds=1),
    }
    ok, err = auth_service.validate_code("a@b.com", "123456")
    assert ok is False
    assert "expired" in err.lower()


def test_validate_code_rejects_wrong_code():
    auth_service.verify_codes["a@b.com"] = {
        "code": "123456",
        "expires": datetime.now(UTC) + timedelta(minutes=5),
    }
    ok, err = auth_service.validate_code("a@b.com", "000000")
    assert ok is False
    assert "Invalid" in err


def test_send_verification_code_stores_otp(monkeypatch):
    mailer = MagicMock()
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_service.handle_mail",
        lambda _m, email: EmailResponseDTO(
            email=email,
            code_verify="654321",
            received_time=datetime.now(UTC),
        ),
    )
    code = auth_service.send_verification_code(mailer, "a@b.com")
    assert code == "654321"
    assert auth_service.verify_codes["a@b.com"]["code"] == "654321"


def test_send_verification_code_returns_none_on_mail_failure(monkeypatch):
    mailer = MagicMock()
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_service.handle_mail",
        lambda _m, _e: EmailResponseDTO(
            email=None,
            code_verify=None,
            received_time=datetime.now(UTC),
        ),
    )
    assert auth_service.send_verification_code(mailer, "a@b.com") is None
    assert "a@b.com" not in auth_service.verify_codes


def test_remove_code_is_idempotent():
    auth_service.verify_codes["a@b.com"] = {
        "code": "1",
        "expires": datetime.now(UTC) + timedelta(minutes=1),
    }
    auth_service.remove_code("a@b.com")
    auth_service.remove_code("a@b.com")
    assert "a@b.com" not in auth_service.verify_codes


def test_authenticate_user_checks_password():
    hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
    user = SimpleNamespace(password=hashed)
    assert auth_service.authenticate_user(user, "secret") is True
    assert auth_service.authenticate_user(user, "wrong") is False


def test_authenticate_user_prefers_check_password():
    user = SimpleNamespace(
        password="ignored",
        check_password=lambda pw: pw == "ok",
    )
    assert auth_service.authenticate_user(user, "ok") is True
    assert auth_service.authenticate_user(user, "no") is False


def test_create_access_token_is_decodable():
    token = auth_service.create_access_token({"sub": "u1"})
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == "u1"


def test_create_access_token_honors_expires_delta():
    token = auth_service.create_access_token(
        {"sub": "u1"},
        expires_delta=timedelta(minutes=1),
    )
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    assert exp - datetime.now(UTC) < timedelta(minutes=2)
