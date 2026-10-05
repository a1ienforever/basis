import asyncio
import logging

from faststream import FastStream

from src.config import Settings, get_settings
from src.container import create_container
from src.infrastructure.logging import setup_logging
from src.presentation.messaging import setup_routers

logger = logging.getLogger("broker.app")


def create_app(settings: Settings | None = None) -> FastStream:
    """Создать приложение FastStream с подписчиками RabbitMQ.

    Args:
        settings: настройки приложения; по умолчанию берутся из окружения.

    Returns:
        Сконфигурированное приложение FastStream.
    """
    settings = settings or get_settings()
    container = create_container(settings)

    setup_routers(container.broker)
    for stub, provider in container.providers.items():
        container.broker.provider.override(stub, provider)

    app = FastStream(container.broker, logger=logger)
    app.after_shutdown(container.engine.dispose)

    return app


setup_logging(get_settings().log)
app = create_app()

if __name__ == "__main__":
    asyncio.run(app.run())
