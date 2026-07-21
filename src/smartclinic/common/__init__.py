from smartclinic.common.base import Settings, get_settings

__all__ = ["Settings", "get_settings", "AppConfig"]


def __getattr__(name: str):
    if name == "AppConfig":
        return get_settings()
    raise AttributeError(name)
