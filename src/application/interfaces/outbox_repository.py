from typing import Protocol
from uuid import UUID

from src.application.dto import MessageDTO


class OutboxRepository(Protocol):
    """Интерфейс репозитория исходящих сообщений (outbox)."""

    async def add(self, aggregate_id: UUID, queue: str, message: MessageDTO) -> None:
        """Поставить сообщение в очередь на отправку в брокер.

        Args:
            aggregate_id: идентификатор агрегата, к которому относится сообщение.
            queue: имя очереди, в которую сообщение будет опубликовано.
            message: сообщение для отправки.
        """
        ...
