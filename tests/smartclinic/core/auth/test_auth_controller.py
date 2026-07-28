from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from smartclinic.common.base import get_settings
from smartclinic.core.auth import auth_service
from smartclinic.core.auth.auth_controller import (
    login_user_controller,
    register_user_controller,
)
from smartclinic.core.auth.auth_dto import LoginDTO, RegisterUserDTO


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    auth_service.verify_codes.clear()


def test_register_rejects_existing_email():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = MagicMock()
    mailer = MagicMock()
    dto = RegisterUserDTO(
        user_name="alice",
        password="secret",
        email="a@b.com",
    )
    with pytest.raises(HTTPException) as exc:
        register_user_controller(mailer, dto, db)
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail.lower()


def test_register_sends_code_when_otp_missing(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    mailer = MagicMock()
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.send_verification_code",
        lambda _m, _e: "123456",
    )
    dto = RegisterUserDTO(
        user_name="alice",
        password="secret",
        email="a@b.com",
        code_verify=None,
    )
    result = register_user_controller(mailer, dto, db)
    assert "Verification code sent" in result["message"]
    db.add.assert_not_called()


def test_register_fails_when_email_send_fails(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    mailer = MagicMock()
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.send_verification_code",
        lambda _m, _e: None,
    )
    dto = RegisterUserDTO(
        user_name="alice",
        password="secret",
        email="a@b.com",
    )
    with pytest.raises(HTTPException) as exc:
        register_user_controller(mailer, dto, db)
    assert exc.value.status_code == 500


def test_register_rejects_invalid_otp(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    mailer = MagicMock()
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.validate_code",
        lambda _e, _c: (False, "Invalid verification code."),
    )
    dto = RegisterUserDTO(
        user_name="alice",
        password="secret",
        email="a@b.com",
        code_verify="000000",
    )
    with pytest.raises(HTTPException) as exc:
        register_user_controller(mailer, dto, db)
    assert exc.value.status_code == 400


def test_register_creates_user_on_valid_otp(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    mailer = MagicMock()
    removed: list[str] = []

    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.validate_code",
        lambda _e, _c: (True, None),
    )
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.remove_code",
        removed.append,
    )

    dto = RegisterUserDTO(
        user_name="alice",
        password="secret",
        email="a@b.com",
        code_verify="123456",
    )
    result = register_user_controller(mailer, dto, db)
    assert result["message"] == "User registered successfully."
    db.add.assert_called_once()
    db.commit.assert_called_once()
    assert removed == ["a@b.com"]


def test_login_rejects_bad_credentials():
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        login_user_controller(LoginDTO(email="a@b.com", password="wrong"), db)
    assert exc.value.status_code == 401


def test_login_returns_bearer_token(monkeypatch):
    user = SimpleNamespace(
        id="u1",
        user_name="alice",
        email="a@b.com",
        role="user",
        check_password=lambda _p: True,
    )
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = user
    monkeypatch.setattr(
        "smartclinic.core.auth.auth_controller.authenticate_user",
        lambda _u, _p: True,
    )

    result = login_user_controller(LoginDTO(email="a@b.com", password="secret"), db)
    assert result["token_type"] == "bearer"
    payload = jwt.decode(
        result["access_token"],
        get_settings().jwt_secret,
        algorithms=["HS256"],
    )
    assert payload["user_id"] == "u1"
    assert payload["role"] == "user"
