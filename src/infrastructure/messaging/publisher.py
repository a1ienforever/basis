from dataclasses import asdict

from faststream.rabbit import RabbitBroker, RabbitExchange

from src.application.dto import MessageDTO


class RabbitEventPublisher:
    """Издатель событий в RabbitMQ."""

    def __init__(self, broker: RabbitBroker, exchange: RabbitExchange) -> None:
        """Инициализация издателя.

        Args:
            broker: брокер RabbitMQ.
            exchange: exchange, через который публикуются сообщения.
        """
        self._broker = broker
        self._exchange = exchange

    async def publish(self, message: MessageDTO) -> None:
        """Опубликовать сообщение в его очередь через exchange как персистентное.

        Args:
            message: сообщение для публикации.
        """
        await self._broker.publish(
            asdict(message),
            queue=message.queue,
            exchange=self._exchange,
            persist=True,
        )
