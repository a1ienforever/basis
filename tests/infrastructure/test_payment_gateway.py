import asyncio
import random

import pytest

from src.config import GatewaySettings
from src.domain.entities import Payment
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    WebhookUrl,
)
from src.infrastructure.payments.gateway import EmulatedPaymentGateway


def make_payment() -> Payment:
    return Payment.create(
        amount=Amount("100.50"),
        currency=Currency.RUB,
        description=Description("Оплата заказа №42"),
        idempotency_key=IdempotencyKey("order-42"),
        webhook_url=WebhookUrl("https://example.com/hook"),
    )


def make_gateway(success_rate: float) -> EmulatedPaymentGateway:
    return EmulatedPaymentGateway(
        GatewaySettings(min_delay=2, max_delay=5, success_rate=success_rate), random.Random(1)
    )


@pytest.fixture
def delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Перехватить задержки шлюза, чтобы тесты не ждали реальные 2–5 секунд."""
    recorded: list[float] = []

    async def fake_sleep(delay: float) -> None:
        recorded.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    return recorded


@pytest.mark.parametrize(("success_rate", "expected"), [(1.0, True), (0.0, False)])
async def test_result_follows_success_rate(
    delays: list[float], success_rate: float, expected: bool
) -> None:
    assert await make_gateway(success_rate).charge(make_payment()) is expected
    assert len(delays) == 1
    assert 2 <= delays[0] <= 5
