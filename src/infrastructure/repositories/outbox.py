from dataclasses import asdict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import MessageDTO
from src.infrastructure.database.models import OutboxMessageModel


class SQLAlchemyOutboxRepository:
    """Репозиторий исходящих сообщений (outbox) на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: сессия SQLAlchemy текущей единицы работы.
        """
        self._session = session

    async def add(self, aggregate_id: UUID, queue: str, message: MessageDTO) -> None:
        """Сохранить сообщение в outbox в рамках текущей транзакции.

        Args:
            aggregate_id: идентификатор агрегата, к которому относится сообщение.
            queue: имя очереди, в которую сообщение будет опубликовано.
            message: сообщение для отправки.
        """
        self._session.add(
            OutboxMessageModel(
                aggregate_id=aggregate_id,
                event_type=queue,
                payload=asdict(message),
            )
        )
        await self._session.flush()
