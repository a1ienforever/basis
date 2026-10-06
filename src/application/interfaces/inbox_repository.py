from typing import Protocol
from uuid import UUID


class InboxRepository(Protocol):
    """Интерфейс репозитория обработанных входящих сообщений (inbox)."""

    async def create(self, consumer: str, message_id: UUID) -> None:
        """Сохранить сообщение как обработанное потребителем.

        Args:
            consumer: имя потребителя, обработавшего сообщение.
            message_id: идентификатор сообщения в outbox отправителя.

        Raises:
            InboxMessageAlreadyExistsError: сообщение уже сохранено
                этим потребителем.
        """
        ...
