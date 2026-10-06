from decimal import Decimal
from uuid import uuid4

import pytest
from faststream.rabbit import RabbitBroker, TestRabbitBroker

from src.application.exceptions import WebhookDeliveryError
from src.config import ConsumerSettings, RabbitSettings, Settings, get_settings
from src.domain.entities import Payment
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    PaymentStatus,
    WebhookUrl,
)
from src.infrastructure.messaging.queues import create_topology
from src.presentation import dependencies as deps
from src.presentation.messaging import setup_routers
from tests.fakes import FakePaymentGateway, FakeUnitOfWork, FakeWebhookSender

SETTINGS = Settings(consumer=ConsumerSettings(max_attempts=3, retry_delay=0))
TOPOLOGY = create_topology(RabbitSettings())


def make_broker(uow: FakeUnitOfWork, webhooks: FakeWebhookSender) -> RabbitBroker:
    broker = RabbitBroker()
    setup_routers(broker, TOPOLOGY.queue, TOPOLOGY.exchange)
    gateway = FakePaymentGateway()
    for stub, provider in {
        deps.get_uow: lambda: uow,
        deps.get_payment_gateway: lambda: gateway,
        deps.get_webhook_sender: lambda: webhooks,
        get_settings: lambda: SETTINGS,
    }.items():
        broker.provider.override(stub, provider)
    return broker


async def add_payment(uow: FakeUnitOfWork) -> Payment:
    return await uow.repository("payments").add(
        Payment.create(
            amount=Amount(Decimal("100.50")),
            currency=Currency.RUB,
            description=Description(""),
            idempotency_key=IdempotencyKey("order-42"),
            webhook_url=WebhookUrl("https://example.com/hook"),
        )
    )


async def publish(broker: RabbitBroker, payment: Payment) -> None:
    await broker.publish(
        {"payment_id": str(payment.id)},
        queue=TOPOLOGY.queue,
        exchange=TOPOLOGY.exchange,
        message_id=str(uuid4()),
    )


async def test_message_from_queue_is_processed(uow: FakeUnitOfWork) -> None:
    payment = await add_payment(uow)
    webhooks = FakeWebhookSender()

    async with TestRabbitBroker(make_broker(uow, webhooks)) as broker:
        await publish(broker, payment)

    assert payment.status is PaymentStatus.SUCCEEDED
    assert [url for url, _ in webhooks.sent] == ["https://example.com/hook"]


async def test_unprocessed_message_is_rejected(uow: FakeUnitOfWork) -> None:
    payment = await add_payment(uow)
    webhooks = FakeWebhookSender([WebhookDeliveryError("url", "down") for _ in range(3)])

    async with TestRabbitBroker(make_broker(uow, webhooks)) as broker:
        with pytest.raises(WebhookDeliveryError):
            await publish(broker, payment)

    assert webhooks.calls == 3
