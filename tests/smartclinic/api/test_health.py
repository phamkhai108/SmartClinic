from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient):
    assert client.get("/health").json()["status"] == "ok"
