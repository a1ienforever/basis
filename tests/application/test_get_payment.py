from decimal import Decimal
from uuid import uuid4

import pytest

from src.application.use_cases import GetPaymentUseCase
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
from tests.fakes import FakeUnitOfWork


async def test_returns_payment_details(uow: FakeUnitOfWork) -> None:
    payment = await uow.repository("payments").add(
        Payment.create(
            amount=Amount("100.50"),
            currency=Currency.RUB,
            description=Description("Оплата заказа №42"),
            idempotency_key=IdempotencyKey("order-42"),
            webhook_url=WebhookUrl("https://example.com/hook"),
            metadata={"order_id": 42},
        )
    )

    result = await GetPaymentUseCase(uow).execute(payment.id)

    assert result.id == payment.id
    assert result.amount == Decimal("100.50")
    assert result.currency is Currency.RUB
    assert result.description == "Оплата заказа №42"
    assert result.metadata == {"order_id": 42}
    assert result.status is PaymentStatus.PENDING
    assert result.idempotency_key == "order-42"
    assert result.webhook_url == "https://example.com/hook"
    assert result.created_at == payment.created_at
    assert result.processed_at is None


async def test_unknown_payment_raises_not_found(uow: FakeUnitOfWork) -> None:
    with pytest.raises(PaymentNotFoundError):
        await GetPaymentUseCase(uow).execute(uuid4())
