from src.application.interfaces import EventPublisher, UnitOfWork


def get_uow() -> UnitOfWork:
    raise NotImplementedError


def get_event_publisher() -> EventPublisher:
    raise NotImplementedError
