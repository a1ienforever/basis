from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import InboxMessageAlreadyExistsError
from src.infrastructure.database.models import InboxMessageModel


class SQLAlchemyInboxRepository:
    """Репозиторий обработанных входящих сообщений (inbox) на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: сессия SQLAlchemy текущей единицы работы.
        """
        self._session = session

    async def create(self, consumer: str, message_id: UUID) -> None:
        """Сохранить сообщение в inbox в рамках текущей транзакции.

        Вставка выполняется в savepoint, поэтому дубликат не обрывает
        внешнюю транзакцию.

        Args:
            consumer: имя потребителя, обработавшего сообщение.
            message_id: идентификатор сообщения в outbox отправителя.

        Raises:
            InboxMessageAlreadyExistsError: сообщение уже сохранено
                этим потребителем.
        """
        try:
            async with self._session.begin_nested():
                self._session.add(InboxMessageModel(consumer=consumer, message_id=message_id))
        except IntegrityError as exc:
            raise InboxMessageAlreadyExistsError(consumer, message_id) from exc
