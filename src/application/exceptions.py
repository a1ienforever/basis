class ApplicationError(Exception):
    """Базовый класс всех ошибок прикладного слоя."""


class InboxMessageAlreadyExistsError(ApplicationError):
    """Сообщение уже сохранено в inbox этим потребителем.

    Attributes:
        consumer: имя потребителя.
        message_id: идентификатор сообщения.
    """

    def __init__(self, consumer: str, message_id: object) -> None:
        """Инициализация ошибки.

        Args:
            consumer: имя потребителя.
            message_id: идентификатор сообщения.
        """
        super().__init__(f"Inbox message '{message_id}' already exists for consumer '{consumer}'")
        self.consumer = consumer
        self.message_id = message_id


class WebhookDeliveryError(ApplicationError):
    """Webhook-уведомление не доставлено получателю.

    Attributes:
        url: адрес получателя уведомления.
        reason: причина, по которой уведомление не доставлено.
    """

    def __init__(self, url: str, reason: str) -> None:
        """Инициализация ошибки.

        Args:
            url: адрес получателя уведомления.
            reason: причина, по которой уведомление не доставлено.
        """
        super().__init__(f"Webhook to '{url}' is not delivered: {reason}")
        self.url = url
        self.reason = reason
