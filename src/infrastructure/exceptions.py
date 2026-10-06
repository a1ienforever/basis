class InfrastructureError(Exception):
    """Базовый класс всех инфраструктурных ошибок."""


class DatabaseRepositoryNotFoundError(InfrastructureError):
    """Запрошенный репозиторий не зарегистрирован в Unit of Work.

    Attributes:
        name: имя запрошенного репозитория.
    """

    def __init__(self, name: str) -> None:
        """Инициализация ошибки.

        Args:
            name: имя запрошенного репозитория.
        """
        super().__init__(f"Repository '{name}' is not registered in the unit of work")
        self.name = name


class BrokerUnavailableError(InfrastructureError):
    """Брокер сообщений недоступен или не подтвердил приём сообщения."""


class EventPublishError(InfrastructureError):
    """Сообщение не может быть опубликовано. Ошибка сообщения."""
