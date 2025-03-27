from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="smartclinic_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    sender_email: str
    sender_password: str


AppConfig = BaseConfig()
