from typing import Any, Self

from src.application.dto import MessageDTO
from src.application.interfaces import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    """In-memory реализация UoW для тестов.

    Attributes:
        repositories: репозитории, доступные по имени.
        committed: был ли вызван коммит.
    """

    def __init__(self, repositories: dict[str, Any] | None = None) -> None:
        """Инициализация UoW.

        Args:
            repositories: репозитории, доступные по имени.
        """
        self.repositories = repositories or {}
        self.committed = False

    async def __aenter__(self) -> Self:
        """Войти в контекст.

        Returns:
            Текущий экземпляр UoW.
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Выйти из контекста: зафиксировать изменения, если не было ошибки.

        Args:
            exc_type: тип исключения, если оно возникло в контексте.
            exc_val: экземпляр исключения, если оно возникло в контексте.
            exc_tb: трассировка исключения, если оно возникло в контексте.
        """
        if exc_type is None:
            await self.commit()

    async def commit(self) -> None:
        """Отметить, что транзакция зафиксирована."""
        self.committed = True

    async def rollback(self) -> None:
        """Откатить транзакцию (ничего не делает)."""
        return None

    def repository(self, name: str) -> Any:
        """Получить репозиторий по имени.

        Args:
            name: имя репозитория.

        Returns:
            Экземпляр репозитория.
        """
        return self.repositories[name]


class FakeEventPublisher:
    """Издатель событий для тестов: накапливает сообщения в памяти.

    Attributes:
        messages: опубликованные сообщения в порядке публикации.
    """

    def __init__(self) -> None:
        """Инициализация издателя."""
        self.messages: list[MessageDTO] = []

    async def publish(self, message: MessageDTO) -> None:
        """Сохранить сообщение в списке опубликованных.

        Args:
            message: сообщение для публикации.
        """
        self.messages.append(message)
