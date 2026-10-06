from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.auth import AuthSettings
from src.config.consumer import ConsumerSettings
from src.config.gateway import GatewaySettings
from src.config.log import LogSettings
from src.config.outbox import OutboxSettings
from src.config.postgres import PostgresSettings
from src.config.rabbit import RabbitSettings


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения и `.env`.

    Attributes:
        app_name: имя приложения.
        debug: режим отладки.
        auth: настройки аутентификации HTTP API.
        postgres: настройки подключения к PostgreSQL.
        rabbit: настройки подключения к RabbitMQ.
        outbox: настройки relay сообщений outbox.
        consumer: настройки потребителя новых платежей.
        gateway: настройки эмулятора платёжного шлюза.
        log: настройки логирования.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
    )

    app_name: str = "basis"
    debug: bool = False
    auth: AuthSettings = AuthSettings()
    postgres: PostgresSettings = PostgresSettings()
    rabbit: RabbitSettings = RabbitSettings()
    outbox: OutboxSettings = OutboxSettings()
    consumer: ConsumerSettings = ConsumerSettings()
    gateway: GatewaySettings = GatewaySettings()
    log: LogSettings = LogSettings()


@lru_cache
def get_settings() -> Settings:
    """Получить настройки приложения.

    Результат кэшируется: настройки читаются один раз за время жизни процесса.

    Returns:
        Настройки приложения.
    """
    return Settings()
