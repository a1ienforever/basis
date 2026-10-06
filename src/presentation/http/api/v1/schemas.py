from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.value_objects import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
    """Тело запроса на создание платежа.

    Attributes:
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        metadata: произвольная дополнительная информация.
        webhook_url: адрес для уведомления о результате.
    """

    amount: Decimal
    currency: Currency
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class CreatePaymentResponse(BaseModel):
    """Ответ на запрос создания платежа.

    Attributes:
        payment_id: уникальный идентификатор платежа.
        status: текущий статус платежа.
        created_at: дата и время создания платежа.
    """

    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    """Детальная информация о платеже.

    Attributes:
        payment_id: уникальный идентификатор платежа.
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        metadata: произвольная дополнительная информация.
        status: текущий статус платежа.
        idempotency_key: ключ идемпотентности, переданный клиентом.
        webhook_url: адрес для уведомления о результате.
        created_at: дата и время создания платежа.
        processed_at: дата и время обработки платежа; `None`, пока платёж
            не обработан.
    """

    payment_id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
