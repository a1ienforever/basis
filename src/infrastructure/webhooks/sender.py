from typing import Any

import httpx

from src.application.exceptions import WebhookDeliveryError
from src.application.interfaces import WebhookSender


class HttpxWebhookSender(WebhookSender):
    """Отправитель webhook-уведомлений по HTTP на httpx."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Инициализация отправителя.

        Args:
            client: HTTP-клиент с настроенным временем ожидания ответа.
        """
        self._client = client

    async def send(self, url: str, payload: dict[str, Any]) -> None:
        """Отправить уведомление POST-запросом с телом в формате JSON.

        Args:
            url: адрес получателя уведомления.
            payload: тело уведомления.

        Raises:
            WebhookDeliveryError: получатель недоступен, не ответил вовремя
                или ответил кодом, отличным от 2xx.
        """
        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise WebhookDeliveryError(url, str(exc) or type(exc).__name__) from exc
