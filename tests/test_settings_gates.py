import pytest
from fastapi import HTTPException

from smartclinic.api.dependencies import require_es_config, require_llm_config
from smartclinic.common.base import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_missing_es_raises_503(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    monkeypatch.setenv("SMARTCLINIC_ES_HOST", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_es_config()
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "MISSING_CONFIG"


def test_missing_llm_lists_keys(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./example.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_URL", "")
    monkeypatch.setenv("SMARTCLINIC_OPENAI_API_KEY", "")
    monkeypatch.setenv("SMARTCLINIC_MODEL_LLM_ID", "")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as exc:
        require_llm_config()
    assert "SMARTCLINIC_OPENAI_API_URL" in exc.value.detail["keys"]
