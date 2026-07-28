from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from smartclinic.core.user.user_service import get_all_users, update_user_role


def test_update_user_role_rejects_unknown_user():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError, match="User not found"):
        update_user_role("missing", "doctor", db)


def test_update_user_role_rejects_invalid_role():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = MagicMock()
    with pytest.raises(ValueError, match="Invalid role"):
        update_user_role("u1", "admin", db)


def test_update_user_role_happy_path():
    db = MagicMock()
    user = MagicMock()
    user.role = "user"
    db.query.return_value.filter.return_value.first.return_value = user
    result = update_user_role("u1", "doctor", db)
    assert result is user
    assert user.role == "doctor"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_get_all_users_maps_dto():
    db = MagicMock()
    row = MagicMock()
    row.id = "u1"
    row.user_name = "alice"
    row.email = "a@b.com"
    row.role = "user"
    db.query.return_value.all.return_value = [row]
    users = get_all_users(db)
    assert len(users) == 1
    assert users[0].id == "u1"
    assert users[0].email == "a@b.com"
    assert users[0].role == "user"
