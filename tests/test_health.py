from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from smartclinic.common.base import get_settings


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    # Import after env so module-level get_settings() succeeds.
    from smartclinic.api import main as main_mod

    main_mod.settings = get_settings()
    with TestClient(main_mod.app) as c:
        yield c
    get_settings.cache_clear()


def test_health_ok(client: TestClient):
    assert client.get("/health").json()["status"] == "ok"
