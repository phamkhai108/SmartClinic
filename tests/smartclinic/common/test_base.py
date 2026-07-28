from __future__ import annotations

from smartclinic.common.base import Settings, get_settings


def test_empty_strings_become_none():
    settings = Settings(
        _env_file=None,
        database_url="sqlite:///./x.db",
        jwt_secret="test-secret-key-16",
        es_host="  ",
        llm_api_url="",
        llm_api_key=None,
        openai_api_url="http://fallback",
        openai_api_key="fallback-key",
        embed_api_url=None,
        embed_api_key=None,
    )
    assert settings.es_host is None
    assert settings.llm_api_url is None
    assert settings.resolved_llm_api_url == "http://fallback"
    assert settings.resolved_llm_api_key == "fallback-key"
    assert settings.resolved_embed_api_url == "http://fallback"


def test_cors_origin_list_splits():
    settings = Settings(
        _env_file=None,
        database_url="sqlite:///./x.db",
        jwt_secret="test-secret-key-16",
        cors_origins="http://a.com, http://b.com ,",
    )
    assert settings.cors_origin_list == ["http://a.com", "http://b.com"]


def test_get_settings_uses_env(monkeypatch):
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", "sqlite:///./env.db")
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.database_url == "sqlite:///./env.db"
    get_settings.cache_clear()
