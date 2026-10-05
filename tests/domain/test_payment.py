from dataclasses import replace
from datetime import UTC, datetime

import pytest

from src.domain.entities import Payment
from src.domain.exceptions import PaymentAlreadyProcessedError
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    PaymentStatus,
    WebhookUrl,
)
from src.infrastructure.database.models import PaymentModel


@pytest.fixture
def payment() -> Payment:
    return Payment.create(
        amount=Amount("100.50"),
        currency=Currency.RUB,
        description=Description("Оплата заказа №42"),
        idempotency_key=IdempotencyKey("order-42"),
        webhook_url=WebhookUrl("https://example.com/hook"),
        metadata={"order_id": 42},
    )


def test_create_returns_pending_payment(payment: Payment) -> None:
    assert payment.status is PaymentStatus.PENDING
    assert payment.created_at is None
    assert payment.processed_at is None
    assert payment.metadata == {"order_id": 42}


def test_create_defaults_to_empty_metadata() -> None:
    payment = Payment.create(
        amount=Amount("1"),
        currency=Currency.USD,
        description=Description(""),
        idempotency_key=IdempotencyKey("key"),
        webhook_url=WebhookUrl("https://example.com/hook"),
    )

    assert payment.metadata == {}


@pytest.mark.parametrize(
    ("method", "status"),
    [("mark_succeeded", PaymentStatus.SUCCEEDED), ("mark_failed", PaymentStatus.FAILED)],
)
def test_processing_sets_status_and_processed_at(
    payment: Payment, method: str, status: PaymentStatus
) -> None:
    getattr(payment, method)()

    assert payment.status is status
    assert payment.processed_at is not None
    assert payment.processed_at.tzinfo is UTC


@pytest.mark.parametrize("method", ["mark_succeeded", "mark_failed"])
def test_processed_payment_cannot_be_processed_again(payment: Payment, method: str) -> None:
    payment.mark_succeeded()

    with pytest.raises(PaymentAlreadyProcessedError):
        getattr(payment, method)()

    assert payment.status is PaymentStatus.SUCCEEDED


def test_model_round_trip_preserves_entity(payment: Payment) -> None:
    payment.mark_failed()

    restored = PaymentModel.from_entity(payment).to_entity()

    assert restored == payment
    assert isinstance(restored.amount, Amount)
    assert isinstance(restored.webhook_url, WebhookUrl)


def test_new_payment_leaves_created_at_to_database(payment: Payment) -> None:
    model = PaymentModel.from_entity(payment)

    assert model.created_at is None
    assert PaymentModel.__table__.c.created_at.server_default is not None


def test_model_round_trip_preserves_created_at(payment: Payment) -> None:
    saved = replace(payment, created_at=datetime(2026, 10, 5, 12, 0, tzinfo=UTC))

    restored = PaymentModel.from_entity(saved).to_entity()

    assert restored == saved
