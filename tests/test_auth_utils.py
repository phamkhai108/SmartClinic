from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import bcrypt
import jwt
import pytest

from smartclinic.common.base import get_settings
from smartclinic.core.auth import auth_service


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


def test_authenticate_user_checks_password():
    hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
    user = SimpleNamespace(password=hashed)
    assert auth_service.authenticate_user(user, "secret") is True
    assert auth_service.authenticate_user(user, "wrong") is False


def test_create_access_token_is_decodable():
    token = auth_service.create_access_token({"sub": "u1"})
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == "u1"
