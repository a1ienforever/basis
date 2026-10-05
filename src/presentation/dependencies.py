from src.application.interfaces import EventPublisher, UnitOfWork


def get_uow() -> UnitOfWork:
    """Заглушка зависимости UoW; реализация подставляется контейнером.

    Returns:
        Экземпляр Unit of Work.

    Raises:
        NotImplementedError: зависимость не переопределена.
    """
    raise NotImplementedError


def get_event_publisher() -> EventPublisher:
    """Заглушка зависимости издателя событий; реализация подставляется контейнером.

    Returns:
        Издатель событий.

    Raises:
        NotImplementedError: зависимость не переопределена.
    """
    raise NotImplementedError
