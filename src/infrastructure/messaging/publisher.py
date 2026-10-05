from dataclasses import asdict

from faststream.rabbit import RabbitBroker

from src.application.dto import MessageDTO


class RabbitEventPublisher:
    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker

    async def publish(self, message: MessageDTO) -> None:
        await self._broker.publish(asdict(message), queue=message.queue, persist=True)
