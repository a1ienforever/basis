from abc import ABC, abstractmethod
from typing import Any


class WebhookSender(ABC):
    """Интерфейс отправки webhook-уведомлений."""

    @abstractmethod
    async def send(self, url: str, payload: dict[str, Any]) -> None:
        """Отправить уведомление на указанный адрес.

        Args:
            url: адрес получателя уведомления.
            payload: тело уведомления.

        Raises:
            WebhookDeliveryError: получатель недоступен или не подтвердил
                приём уведомления.
        """
        ...
