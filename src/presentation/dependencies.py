from src.application.interfaces import PaymentGateway, UnitOfWork, WebhookSender


def get_uow() -> UnitOfWork:
    """Заглушка зависимости UoW; реализация подставляется контейнером.

    Returns:
        Экземпляр Unit of Work.

    Raises:
        NotImplementedError: зависимость не переопределена.
    """
    raise NotImplementedError


def get_payment_gateway() -> PaymentGateway:
    """Заглушка зависимости платёжного шлюза; реализация подставляется контейнером.

    Returns:
        Платёжный шлюз.

    Raises:
        NotImplementedError: зависимость не переопределена.
    """
    raise NotImplementedError


def get_webhook_sender() -> WebhookSender:
    """Заглушка зависимости отправителя webhook; реализация подставляется контейнером.

    Returns:
        Отправитель webhook-уведомлений.

    Raises:
        NotImplementedError: зависимость не переопределена.
    """
    raise NotImplementedError
