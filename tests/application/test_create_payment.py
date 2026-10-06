from decimal import Decimal

from src.application.dto import CreatePaymentDTO, PaymentCreatedMessage
from src.application.use_cases import CreatePaymentUseCase
from src.config import RabbitSettings, Settings
from src.domain.value_objects import Currency, PaymentStatus
from tests.fakes import FakeUnitOfWork

SETTINGS = Settings(rabbit=RabbitSettings(queue="payments.test"))


def make_data(**overrides: object) -> CreatePaymentDTO:
    fields: dict[str, object] = {
        "amount": Decimal("100.50"),
        "currency": Currency.RUB,
        "description": "Оплата заказа №42",
        "metadata": {"order_id": 42},
        "webhook_url": "https://example.com/hook",
        "idempotency_key": "order-42",
    }
    return CreatePaymentDTO(**(fields | overrides))


async def test_creates_payment_and_outbox_message(uow: FakeUnitOfWork) -> None:
    result = await CreatePaymentUseCase(uow, SETTINGS).execute(make_data())

    payment = uow.repository("payments").payments["order-42"]
    assert result.id == payment.id
    assert result.status is PaymentStatus.PENDING
    assert result.created_at == payment.created_at
    assert payment.amount == Decimal("100.50")
    assert payment.metadata == {"order_id": 42}
    assert uow.repository("outbox").messages == [
        (payment.id, "payments.test", PaymentCreatedMessage(payment_id=str(payment.id)))
    ]
    assert uow.committed


async def test_repeated_key_returns_existing_payment(uow: FakeUnitOfWork) -> None:
    use_case = CreatePaymentUseCase(uow, SETTINGS)
    first = await use_case.execute(make_data())

    second = await use_case.execute(make_data(amount=Decimal("999")))

    assert second == first
    assert len(uow.repository("payments").payments) == 1
    assert len(uow.repository("outbox").messages) == 1
