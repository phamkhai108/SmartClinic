from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from smartclinic.core.user.user_service import update_user_role


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
