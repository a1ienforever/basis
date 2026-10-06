from typing import Any
from uuid import uuid4

import pytest
from aiormq.abc import DeliveredMessage
from aiormq.exceptions import AMQPConnectionError, DeliveryError, PublishError
from faststream.rabbit import RabbitExchange
from pamqp.commands import Basic
from pamqp.header import ContentHeader

from src.infrastructure.exceptions import BrokerUnavailableError, EventPublishError
from src.infrastructure.messaging.outbox_publisher import RabbitOutboxPublisher


class StubBroker:
    """Брокер-заглушка: запоминает параметры публикации и возбуждает заданную ошибку."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[dict[str, Any]] = []

    async def publish(self, message: Any, **options: Any) -> None:
        self.calls.append({"message": message, **options})
        if self.error is not None:
            raise self.error


def make_publisher(broker: StubBroker) -> RabbitOutboxPublisher:
    return RabbitOutboxPublisher(broker, RabbitExchange("payments"), timeout=5.0)  # type: ignore[arg-type]


def unroutable() -> PublishError:
    frame = Basic.Return(reply_code=312, reply_text="NO_ROUTE", routing_key="payments.new")
    message = DeliveredMessage(delivery=frame, header=ContentHeader(), body=b"", channel=None)  # type: ignore[arg-type]
    return PublishError(message, frame)


async def test_message_is_published_persistent_mandatory_with_stable_id() -> None:
    broker = StubBroker()
    message_id = uuid4()

    await make_publisher(broker).publish(message_id, "payments.new", {"payment_id": "42"})

    (call,) = broker.calls
    assert call["message"] == {"payment_id": "42"}
    assert call["routing_key"] == "payments.new"
    assert call["message_id"] == str(message_id)
    assert call["persist"] is True
    assert call["mandatory"] is True


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (AMQPConnectionError("connection lost"), BrokerUnavailableError),
        (TimeoutError(), BrokerUnavailableError),
        (DeliveryError(None, Basic.Nack()), BrokerUnavailableError),
        (unroutable(), EventPublishError),
        (TypeError("not serializable"), EventPublishError),
    ],
)
async def test_broker_errors_are_classified(error: Exception, expected: type[Exception]) -> None:
    with pytest.raises(expected):
        await make_publisher(StubBroker(error)).publish(uuid4(), "payments.new", {})
