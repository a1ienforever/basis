from typing import Any, Self

from src.application.dto import MessageDTO
from src.application.interfaces import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, repositories: dict[str, Any] | None = None) -> None:
        self.repositories = repositories or {}
        self.committed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            await self.commit()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None

    def repository(self, name: str) -> Any:
        return self.repositories[name]


class FakeEventPublisher:
    def __init__(self) -> None:
        self.messages: list[MessageDTO] = []

    async def publish(self, message: MessageDTO) -> None:
        self.messages.append(message)
