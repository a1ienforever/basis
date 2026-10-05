from abc import ABC, abstractmethod
from typing import Any, Self


class UnitOfWork(ABC):
    """Интерфейс Unit of Work.

    Предоставляет доступ к репозиториям и управляет границами транзакции.
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Войти в контекст и начать единицу работы.

        Returns:
            Текущий экземпляр UoW.
        """
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Выйти из контекста: зафиксировать изменения или откатить их при ошибке.

        Args:
            exc_type: тип исключения, если оно возникло в контексте.
            exc_val: экземпляр исключения, если оно возникло в контексте.
            exc_tb: трассировка исключения, если оно возникло в контексте.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию."""
        ...

    @abstractmethod
    def repository(self, name: str) -> Any:
        """Получить репозиторий по имени.

        Args:
            name: имя, под которым репозиторий зарегистрирован в UoW.

        Returns:
            Экземпляр репозитория.
        """
        ...
