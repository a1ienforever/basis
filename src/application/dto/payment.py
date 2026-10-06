from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.application.dto.base import MessageDTO
from src.domain.value_objects import Currency, PaymentStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePaymentDTO:
    """Входные данные для создания платежа.

    Attributes:
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        webhook_url: адрес для уведомления о результате.
        idempotency_key: ключ идемпотентности, переданный клиентом.
        metadata: произвольная дополнительная информация.
    """

    amount: Decimal
    currency: Currency
    description: str
    webhook_url: str
    idempotency_key: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentDTO:
    """Результат создания платежа.

    Attributes:
        id: уникальный идентификатор платежа.
        status: текущий статус платежа.
        created_at: дата и время создания платежа.
    """

    id: UUID
    status: PaymentStatus
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentDetailsDTO:
    """Детальная информация о платеже.

    Attributes:
        id: уникальный идентификатор платежа.
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        metadata: произвольная дополнительная информация.
        status: текущий статус платежа.
        webhook_url: адрес для уведомления о результате.
        created_at: дата и время создания платежа.
        processed_at: дата и время обработки платежа; `None`, пока платёж
            не обработан.
    """

    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    status: PaymentStatus
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None


@dataclass(frozen=True, slots=True)
class PaymentCreatedMessage(MessageDTO):
    """Сообщение о создании платежа, ожидающего обработки.

    Очередь не задаётся: её имя берётся из настроек при записи в outbox.

    Attributes:
        payment_id: идентификатор созданного платежа.
    """

    payment_id: str
