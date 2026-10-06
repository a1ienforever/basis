import logging
from uuid import uuid4

import pytest

from src.config import OutboxSettings
from src.infrastructure.database.models import OutboxMessageModel, OutboxStatus
from src.infrastructure.exceptions import BrokerUnavailableError, EventPublishError
from src.infrastructure.messaging.outbox_relay import OutboxRelay
from tests.fakes import FakeOutboxPublisher, FakeUnitOfWork

SETTINGS = OutboxSettings(max_attempts=2)


def add_row(uow: FakeUnitOfWork) -> OutboxMessageModel:
    row = OutboxMessageModel(
        id=uuid4(),
        aggregate_id=uuid4(),
        event_type="payments.new",
        payload={"payment_id": "42"},
        status=OutboxStatus.PENDING,
        attempts=0,
    )
    uow.repository("outbox").rows.append(row)
    return row


def make_relay(uow: FakeUnitOfWork, publisher: FakeOutboxPublisher) -> OutboxRelay:
    return OutboxRelay(lambda: uow, publisher, SETTINGS)


async def test_confirmed_message_is_marked_published(uow: FakeUnitOfWork) -> None:
    row = add_row(uow)
    publisher = FakeOutboxPublisher()

    assert await make_relay(uow, publisher).process_batch()

    assert publisher.published == [(row.id, "payments.new", {"payment_id": "42"})]
    assert row.status is OutboxStatus.PUBLISHED
    assert row.published_at is not None
    assert uow.committed


async def test_event_error_spends_attempts_then_fails_with_alert(
    uow: FakeUnitOfWork, caplog: pytest.LogCaptureFixture
) -> None:
    row = add_row(uow)
    relay = make_relay(uow, FakeOutboxPublisher([EventPublishError("unroutable")] * 2))

    await relay.process_batch()

    assert (row.status, row.attempts, row.error) == (OutboxStatus.PENDING, 1, "unroutable")

    with caplog.at_level(logging.CRITICAL, logger="outbox.alert"):
        await relay.process_batch()

    assert (row.status, row.attempts) == (OutboxStatus.FAILED, 2)
    assert row.published_at is None
    alerts = [record for record in caplog.records if record.name == "outbox.alert"]
    assert len(alerts) == 1
    assert str(row.id) in alerts[0].getMessage()


async def test_unavailable_broker_spends_no_attempts(uow: FakeUnitOfWork) -> None:
    first, second = add_row(uow), add_row(uow)
    publisher = FakeOutboxPublisher([BrokerUnavailableError("connection lost")])

    assert not await make_relay(uow, publisher).process_batch()

    assert publisher.published == []
    for row in (first, second):
        assert (row.status, row.attempts, row.error) == (OutboxStatus.PENDING, 0, None)
