from typing import Protocol

from src.application.dto import MessageDTO


class EventPublisher(Protocol):
    """Интерфейс публикации событий в брокер сообщений."""

    async def publish(self, message: MessageDTO) -> None:
        """Опубликовать сообщение в его очередь.

        Args:
            message: сообщение для публикации.
        """
        ...
