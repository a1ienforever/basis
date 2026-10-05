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
from src.infrastructure.messaging.publisher import RabbitEventPublisher
from src.presentation import dependencies as deps


@dataclass(frozen=True, slots=True)
class Container:
    engine: AsyncEngine
    broker: RabbitBroker
    providers: dict[Callable[..., Any], Callable[..., Any]]


def create_container(settings: Settings) -> Container:
    engine = create_engine(settings.postgres.url, echo=settings.debug)
    session_factory = create_session_factory(engine)

    broker = create_broker(settings.rabbit)
    publisher = RabbitEventPublisher(broker)

    def get_uow() -> UnitOfWork:
        return AppUnitOfWork(session_factory)

    def get_event_publisher() -> EventPublisher:
        return publisher

    providers: dict[Callable[..., Any], Callable[..., Any]] = {
        deps.get_uow: get_uow,
        deps.get_event_publisher: get_event_publisher,
    }

    return Container(engine=engine, broker=broker, providers=providers)
