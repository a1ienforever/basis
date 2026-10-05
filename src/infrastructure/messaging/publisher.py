from dataclasses import asdict

from faststream.rabbit import RabbitBroker

from src.application.dto import MessageDTO


class RabbitEventPublisher:
    """Издатель событий в RabbitMQ."""

    def __init__(self, broker: RabbitBroker) -> None:
        """Инициализация издателя.

        Args:
            broker: брокер RabbitMQ.
        """
        self._broker = broker

    async def publish(self, message: MessageDTO) -> None:
        """Опубликовать сообщение в его очередь как персистентное.

        Args:
            message: сообщение для публикации.
        """
        await self._broker.publish(asdict(message), queue=message.queue, persist=True)
