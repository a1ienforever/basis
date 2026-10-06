import asyncio
import logging

from faststream import FastStream

from src.config import Settings, get_settings
from src.container import Container, create_container
from src.infrastructure.logging import setup_logging
from src.infrastructure.messaging.queues import declare_topology
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

    setup_routers(container.broker, container.topology.queue, container.topology.exchange)
    for stub, provider in container.providers.items():
        container.broker.provider.override(stub, provider)

    app = FastStream(container.broker, logger=logger)
    setup_lifecycle(app, container)

    return app


def setup_lifecycle(app: FastStream, container: Container) -> None:
    """Подключить к broker-app объявление топологии, запуск relay и освобождение ресурсов.

    Args:
        app: приложение FastStream.
        container: контейнер зависимостей приложения.
    """

    relay_tasks: list[asyncio.Task[None]] = []

    @app.after_startup
    async def declare_payments_topology() -> None:
        """Объявить exchange и очереди платежей после подключения брокера."""
        await declare_topology(container.broker, container.topology)

    @app.after_startup
    async def start_outbox_relay() -> None:
        """Запустить relay сообщений outbox фоновой задачей."""
        relay_tasks.append(asyncio.create_task(container.relay.run()))

    @app.on_shutdown
    async def stop_outbox_relay() -> None:
        """Остановить relay и дождаться завершения текущей пачки до закрытия брокера."""
        container.relay.stop()
        await asyncio.gather(*relay_tasks)

    @app.after_shutdown
    async def release_resources() -> None:
        """Закрыть HTTP-клиент и пул соединений с БД после остановки брокера."""
        await container.http_client.aclose()
        await container.engine.dispose()


setup_logging(get_settings().log)
app = create_app()

if __name__ == "__main__":
    asyncio.run(app.run())
