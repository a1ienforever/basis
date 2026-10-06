from uuid import UUID

from src.application.exceptions import InboxMessageAlreadyExistsError
from src.application.interfaces import InboxRepository, UnitOfWork


class InboxService:
    """Сервис регистрации обработанных входящих сообщений (inbox)."""

    async def register(self, uow: UnitOfWork, consumer: str, message_id: UUID) -> bool:
        """Зарегистрировать сообщение как обработанное потребителем.

        Args:
            uow: открытый Unit of Work с репозиторием `inbox`.
            consumer: имя потребителя.
            message_id: идентификатор сообщения в outbox отправителя.

        Returns:
            `True`, если сообщение зарегистрировано впервые и его нужно обработать;
            `False`, если потребитель уже обрабатывал его ранее.
        """
        inbox: InboxRepository = uow.repository("inbox")
        try:
            await inbox.create(consumer, message_id)
        except InboxMessageAlreadyExistsError:
            return False
        return True
