import asyncio
import random

import pytest

from src.config import GatewaySettings
from src.infrastructure.payments.gateway import EmulatedPaymentGateway


@pytest.mark.parametrize(("success_rate", "expected"), [(1.0, True), (0.0, False)])
async def test_result_follows_success_rate(
    monkeypatch: pytest.MonkeyPatch, success_rate: float, expected: bool
) -> None:
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    gateway = EmulatedPaymentGateway(
        GatewaySettings(min_delay=2, max_delay=5, success_rate=success_rate), random.Random(1)
    )

    assert await gateway.charge(None) is expected  # type: ignore[arg-type]
    assert len(delays) == 1
    assert 2 <= delays[0] <= 5
