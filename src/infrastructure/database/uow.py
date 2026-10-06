import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.interfaces import UnitOfWork
from src.infrastructure.exceptions import DatabaseRepositoryNotFoundError
from src.infrastructure.repositories import (
    SQLAlchemyInboxRepository,
    SQLAlchemyOutboxRepository,
    SQLAlchemyPaymentRepository,
)

logger = logging.getLogger(__name__)


class SQLAlchemyUnitOfWork(UnitOfWork):
    """Реализация Unit of Work для SQLAlchemy.

    Предоставляет доступ к репозиториям и управляет транзакциями через сессию.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """Инициализация UoW.

        Args:
            session_factory: фабрика сессий SQLAlchemy.
        """
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._repositories: dict[str, Any] = {}

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        """Войти в контекст: создать сессию и зарегистрировать репозитории.

        Returns:
            Текущий экземпляр UoW.
        """
        try:
            self._session = self._session_factory()
            self._register_repositories()
            return self
        except Exception:
            logger.exception("UOW: ошибка инициализации")
            raise

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Выйти из контекста: при ошибке откатить транзакцию, иначе зафиксировать.

        Сессия закрывается в любом случае.

        Args:
            exc_type: тип исключения, если оно возникло в контексте.
            exc_val: экземпляр исключения, если оно возникло в контексте.
            exc_tb: трассировка исключения, если оно возникло в контексте.
        """
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self._session:
                await self._session.close()
            self._session = None
            self._repositories.clear()

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        if not self._session:
            return
        try:
            await self._session.commit()
        except Exception:
            logger.exception("UOW: ошибка commit")
            raise

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        if not self._session:
            return
        try:
            await self._session.rollback()
        except Exception:
            logger.exception("UOW: ошибка rollback")
            raise

    def repository(self, name: str) -> Any:
        """Получить репозиторий по имени.

        Args:
            name: имя, под которым репозиторий зарегистрирован в UoW.

        Returns:
            Экземпляр репозитория.

        Raises:
            DatabaseRepositoryNotFoundError: репозиторий с таким именем
                не зарегистрирован.
        """
        if name not in self._repositories:
            logger.error(
                "UOW: репозиторий не найден: %s. Доступные: %s", name, self._repositories.keys()
            )
            raise DatabaseRepositoryNotFoundError(name)
        return self._repositories[name]

    def _register_repositories(self) -> None:
        """Зарегистрировать репозитории; переопределяется в наследниках."""
        pass


class AppUnitOfWork(SQLAlchemyUnitOfWork):
    """UoW сервиса: регистрирует репозитории приложения."""

    def _register_repositories(self) -> None:
        """Зарегистрировать репозитории приложения."""
        self._repositories["payments"] = SQLAlchemyPaymentRepository(self._session)
        self._repositories["outbox"] = SQLAlchemyOutboxRepository(self._session)
        self._repositories["inbox"] = SQLAlchemyInboxRepository(self._session)
