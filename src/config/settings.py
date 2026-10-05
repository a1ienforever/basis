from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.log import LogSettings
from src.config.postgres import PostgresSettings
from src.config.rabbit import RabbitSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="_",
        extra="ignore",
    )

    app_name: str = "basis"
    debug: bool = False
    postgres: PostgresSettings = PostgresSettings()
    rabbit: RabbitSettings = RabbitSettings()
    log: LogSettings = LogSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
