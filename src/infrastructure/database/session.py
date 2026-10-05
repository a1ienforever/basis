from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(url: URL | str, *, echo: bool = False) -> AsyncEngine:
    """Создать асинхронный движок SQLAlchemy.

    Args:
        url: URL подключения к БД.
        echo: логировать ли выполняемые SQL-запросы.

    Returns:
        Асинхронный движок с проверкой соединений перед использованием.
    """
    return create_async_engine(url, echo=echo, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Создать фабрику асинхронных сессий.

    Args:
        engine: асинхронный движок SQLAlchemy.

    Returns:
        Фабрика сессий, объекты которых не сбрасываются после коммита.
    """
    return async_sessionmaker(engine, expire_on_commit=False)
