from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from smartclinic.api.deps_auth import CurrentUser, get_current_user, require_roles
from smartclinic.common.base import get_settings


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_get_current_user_missing_token():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        get_current_user(None, db)
    assert exc.value.status_code == 401
    assert exc.value.detail["code"] == "UNAUTHORIZED"


def test_get_current_user_empty_credentials():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        get_current_user(_bearer(""), db)
    assert exc.value.status_code == 401


def test_get_current_user_invalid_jwt():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        get_current_user(_bearer("not-a-jwt"), db)
    assert exc.value.status_code == 401
    assert "Invalid or expired" in exc.value.detail["message"]


def test_get_current_user_missing_user_id_claim():
    token = jwt.encode(
        {"email": "a@b.com"},
        get_settings().jwt_secret,
        algorithm="HS256",
    )
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        get_current_user(_bearer(token), db)
    assert exc.value.status_code == 401
    assert "payload" in exc.value.detail["message"].lower()


def test_get_current_user_user_not_found():
    token = jwt.encode(
        {"user_id": "missing"},
        get_settings().jwt_secret,
        algorithm="HS256",
    )
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_current_user(_bearer(token), db)
    assert exc.value.status_code == 401
    assert "not found" in exc.value.detail["message"].lower()


def test_get_current_user_happy_path():
    token = jwt.encode(
        {"user_id": "u1"},
        get_settings().jwt_secret,
        algorithm="HS256",
    )
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = SimpleNamespace(
        id="u1",
        user_name="alice",
        email="a@b.com",
        role="user",
    )
    user = get_current_user(_bearer(token), db)
    assert isinstance(user, CurrentUser)
    assert user.id == "u1"
    assert user.user_name == "alice"
    assert user.email == "a@b.com"
    assert user.role == "user"


def test_require_roles_rejects_disallowed_role():
    checker = require_roles("admin")
    user = CurrentUser(id="u1", user_name="alice", email="a@b.com", role="user")
    with pytest.raises(HTTPException) as exc:
        checker(user)
    assert exc.value.status_code == 403
    assert exc.value.detail["code"] == "FORBIDDEN"


def test_require_roles_allows_matching_role():
    checker = require_roles("admin", "doctor")
    user = CurrentUser(id="u1", user_name="doc", email="d@b.com", role="doctor")
    assert checker(user) is user
