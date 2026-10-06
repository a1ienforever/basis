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
