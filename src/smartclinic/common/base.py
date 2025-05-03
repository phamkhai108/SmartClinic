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
    es_host: str
    openai_api_url: str
    openai_api_key: str
    model_llm_id: str
    model_embed_id: str
    database_url: str


AppConfig = BaseConfig()
