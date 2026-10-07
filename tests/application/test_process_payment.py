from decimal import Decimal
from uuid import uuid4

import pytest

from src.application.exceptions import WebhookDeliveryError
from src.application.use_cases import ProcessPaymentUseCase
from src.config import ConsumerSettings, Settings
from src.domain.entities import Payment
from src.domain.exceptions import PaymentNotFoundError
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    PaymentStatus,
    WebhookUrl,
)
from tests.fakes import FakePaymentGateway, FakeUnitOfWork, FakeWebhookSender

SETTINGS = Settings(consumer=ConsumerSettings(max_attempts=3, retry_delay=0))
WEBHOOK_URL = "https://example.com/hook"


async def add_payment(uow: FakeUnitOfWork) -> Payment:
    return await uow.repository("payments").add(
        Payment.create(
            amount=Amount(Decimal("100.50")),
            currency=Currency.RUB,
            description=Description("Оплата заказа №42"),
            idempotency_key=IdempotencyKey("order-42"),
            webhook_url=WebhookUrl(WEBHOOK_URL),
            metadata={"order_id": 42},
        )
    )


def webhook_error() -> WebhookDeliveryError:
    return WebhookDeliveryError(WEBHOOK_URL, "connection refused")


async def test_successful_charge_marks_payment_succeeded_and_sends_webhook(
    uow: FakeUnitOfWork,
) -> None:
    payment = await add_payment(uow)
    webhooks = FakeWebhookSender()

    await ProcessPaymentUseCase(uow, FakePaymentGateway(), webhooks, SETTINGS).execute(
        uuid4(), payment.id
    )

    assert payment.status is PaymentStatus.SUCCEEDED
    assert payment.processed_at is not None
    assert webhooks.sent == [
        (
            WEBHOOK_URL,
            {
                "payment_id": str(payment.id),
                "status": "succeeded",
                "amount": "100.50",
                "currency": "RUB",
                "description": "Оплата заказа №42",
                "metadata": {"order_id": 42},
                "processed_at": payment.processed_at.isoformat(),
            },
        )
    ]
    assert uow.committed


async def test_declined_charge_marks_payment_failed_and_sends_webhook(
    uow: FakeUnitOfWork,
) -> None:
    payment = await add_payment(uow)
    webhooks = FakeWebhookSender()

    await ProcessPaymentUseCase(uow, FakePaymentGateway(success=False), webhooks, SETTINGS).execute(
        uuid4(), payment.id
    )

    assert payment.status is PaymentStatus.FAILED
    assert [payload["status"] for _, payload in webhooks.sent] == ["failed"]


async def test_gateway_is_called_outside_transaction(uow: FakeUnitOfWork) -> None:
    payment = await add_payment(uow)
    active_during_charge: list[bool] = []

    class ObservingGateway(FakePaymentGateway):
        async def charge(self, payment: Payment) -> bool:
            active_during_charge.append(uow.active)
            return await super().charge(payment)

    await ProcessPaymentUseCase(uow, ObservingGateway(), FakeWebhookSender(), SETTINGS).execute(
        uuid4(), payment.id
    )

    assert active_during_charge == [False]
    assert payment.status is PaymentStatus.SUCCEEDED


async def test_webhook_is_retried_without_charging_again(uow: FakeUnitOfWork) -> None:
    payment = await add_payment(uow)
    gateway = FakePaymentGateway()
    webhooks = FakeWebhookSender([webhook_error(), webhook_error()])

    await ProcessPaymentUseCase(uow, gateway, webhooks, SETTINGS).execute(uuid4(), payment.id)

    assert gateway.charged == [payment.id]
    assert webhooks.calls == 3
    assert len(webhooks.sent) == 1


async def test_error_is_raised_after_max_attempts(uow: FakeUnitOfWork) -> None:
    payment = await add_payment(uow)
    webhooks = FakeWebhookSender([webhook_error() for _ in range(5)])

    with pytest.raises(WebhookDeliveryError):
        await ProcessPaymentUseCase(uow, FakePaymentGateway(), webhooks, SETTINGS).execute(
            uuid4(), payment.id
        )

    assert webhooks.calls == 3
    assert payment.status is PaymentStatus.SUCCEEDED


async def test_redelivered_message_resends_webhook_without_charging_again(
    uow: FakeUnitOfWork,
) -> None:
    payment = await add_payment(uow)
    gateway = FakePaymentGateway()
    webhooks = FakeWebhookSender()
    use_case = ProcessPaymentUseCase(uow, gateway, webhooks, SETTINGS)
    message_id = uuid4()
    await use_case.execute(message_id, payment.id)

    await use_case.execute(message_id, payment.id)

    assert gateway.charged == [payment.id]
    assert len(webhooks.sent) == 2


async def test_missing_payment_is_not_retried(uow: FakeUnitOfWork) -> None:
    webhooks = FakeWebhookSender()

    with pytest.raises(PaymentNotFoundError):
        await ProcessPaymentUseCase(uow, FakePaymentGateway(), webhooks, SETTINGS).execute(
            uuid4(), uuid4()
        )

    assert webhooks.calls == 0
