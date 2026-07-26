from __future__ import annotations

from smartclinic.common.base import Settings, get_settings

__all__ = ["AppConfig", "Settings", "get_settings"]


def __getattr__(name: str):
    if name == "AppConfig":
        return get_settings()
    raise AttributeError(name)
