from typing import Protocol

from src.application.dto import MessageDTO


class EventPublisher(Protocol):
    async def publish(self, message: MessageDTO) -> None: ...
