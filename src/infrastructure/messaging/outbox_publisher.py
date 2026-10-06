from typing import Any
from uuid import UUID

from aiormq.exceptions import ChannelInvalidStateError, DeliveryError, PublishError
from faststream.exceptions import IncorrectState
from faststream.rabbit import RabbitBroker, RabbitExchange

from src.infrastructure.exceptions import BrokerUnavailableError, EventPublishError

BROKER_ERRORS = (OSError, TimeoutError, ChannelInvalidStateError, IncorrectState)


class RabbitOutboxPublisher:
    """Издатель сообщений outbox в RabbitMQ с подтверждением доставки."""

    def __init__(self, broker: RabbitBroker, exchange: RabbitExchange, timeout: float) -> None:
        """Инициализация издателя.

        Args:
            broker: брокер RabbitMQ; его канал должен работать с publisher confirms
                и возбуждать исключение при возврате сообщения.
            exchange: exchange, через который публикуются сообщения.
            timeout: время ожидания подтверждения брокера в секундах.
        """
        self._broker = broker
        self._exchange = exchange
        self._timeout = timeout

    async def publish(self, message_id: UUID, routing_key: str, payload: dict[str, Any]) -> None:
        """Опубликовать персистентное сообщение и дождаться подтверждения брокера.

        Args:
            message_id: стабильный идентификатор сообщения для дедупликации у потребителя.
            routing_key: ключ маршрутизации сообщения.
            payload: тело сообщения.

        Raises:
            BrokerUnavailableError: нет соединения с брокером, подтверждение
                не получено вовремя или брокер отклонил сообщение.
            EventPublishError: сообщение возвращено как немаршрутизируемое
                или не может быть отправлено по другой причине.
        """
        try:
            await self._broker.publish(
                payload,
                exchange=self._exchange,
                routing_key=routing_key,
                mandatory=True,
                persist=True,
                message_id=str(message_id),
                timeout=self._timeout,
            )
        except PublishError as exc:
            raise EventPublishError(f"Message is unroutable: {exc}") from exc
        except (DeliveryError, *BROKER_ERRORS) as exc:
            raise BrokerUnavailableError(str(exc) or type(exc).__name__) from exc
        except Exception as exc:
            raise EventPublishError(str(exc) or type(exc).__name__) from exc
