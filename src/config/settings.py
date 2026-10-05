from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.log import LogSettings
from src.config.postgres import PostgresSettings
from src.config.rabbit import RabbitSettings


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения и `.env`.

    Attributes:
        app_name: имя приложения.
        debug: режим отладки.
        postgres: настройки подключения к PostgreSQL.
        rabbit: настройки подключения к RabbitMQ.
        log: настройки логирования.
    """

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
    """Получить настройки приложения.

    Результат кэшируется: настройки читаются один раз за время жизни процесса.

    Returns:
        Настройки приложения.
    """
    return Settings()
