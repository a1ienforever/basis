from datetime import datetime
from uuid import UUID

from httpx import AsyncClient

from tests.fakes import FakeUnitOfWork

URL = "/api/v1/payments"
HEADERS = {"Idempotency-Key": "order-42"}
BODY = {
    "amount": "100.50",
    "currency": "RUB",
    "description": "Оплата заказа №42",
    "metadata": {"order_id": 42},
    "webhook_url": "https://example.com/hook",
}


async def test_create_payment_is_accepted(client: AsyncClient, uow: FakeUnitOfWork) -> None:
    response = await client.post(URL, json=BODY, headers=HEADERS)

    assert response.status_code == 202
    data = response.json()
    assert set(data) == {"payment_id", "status", "created_at"}
    assert data["status"] == "pending"
    datetime.fromisoformat(data["created_at"])
    assert [aggregate_id for aggregate_id, _, _ in uow.repository("outbox").messages] == [
        UUID(data["payment_id"])
    ]


async def test_missing_idempotency_key_is_rejected(client: AsyncClient) -> None:
    response = await client.post(URL, json=BODY)

    assert response.status_code == 422
