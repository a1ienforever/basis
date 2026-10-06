from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncEngine

from src.application.interfaces import EventPublisher, UnitOfWork
from src.config import Settings
from src.infrastructure.database.session import create_engine, create_session_factory
from src.infrastructure.database.uow import AppUnitOfWork
from src.infrastructure.messaging.broker import create_broker
from src.infrastructure.messaging.outbox_publisher import RabbitOutboxPublisher
from src.infrastructure.messaging.outbox_relay import OutboxRelay
from src.infrastructure.messaging.publisher import RabbitEventPublisher
from src.infrastructure.messaging.queues import PaymentsTopology, create_topology
from src.presentation import dependencies as deps


@dataclass(frozen=True, slots=True)
class Container:
    """Контейнер инфраструктурных зависимостей приложения.

    Attributes:
        engine: движок SQLAlchemy.
        broker: брокер RabbitMQ.
        topology: exchange и очереди платежей.
        relay: relay сообщений outbox; запускается только в broker-приложении.
        providers: соответствие заглушек зависимостей их реализациям.
    """

    engine: AsyncEngine
    broker: RabbitBroker
    topology: PaymentsTopology
    relay: OutboxRelay
    providers: dict[Callable[..., Any], Callable[..., Any]]


def create_container(settings: Settings) -> Container:
    """Собрать контейнер зависимостей.

    Args:
        settings: настройки приложения.

    Returns:
        Контейнер зависимостей.
    """
    engine = create_engine(settings.postgres.url, echo=settings.debug)
    session_factory = create_session_factory(engine)

    broker = create_broker(settings.rabbit)
    topology = create_topology(settings.rabbit)
    publisher = RabbitEventPublisher(broker, topology.exchange)

    def get_uow() -> UnitOfWork:
        """Создать новый UoW на общей фабрике сессий."""
        return AppUnitOfWork(session_factory)

    def get_event_publisher() -> EventPublisher:
        """Вернуть общий издатель событий."""
        return publisher

    relay = OutboxRelay(
        uow_factory=get_uow,
        publisher=RabbitOutboxPublisher(
            broker, topology.exchange, timeout=settings.outbox.publish_timeout
        ),
        settings=settings.outbox,
    )

    providers: dict[Callable[..., Any], Callable[..., Any]] = {
        deps.get_uow: get_uow,
        deps.get_event_publisher: get_event_publisher,
    }

    return Container(
        engine=engine, broker=broker, topology=topology, relay=relay, providers=providers
    )
