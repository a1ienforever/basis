from datetime import datetime
from decimal import Decimal
from typing import Any, Self
from uuid import UUID

from sqlalchemy import DateTime, Enum, Numeric, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities import Payment
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    PaymentStatus,
    WebhookUrl,
)
from src.infrastructure.database.base import Base


class PaymentModel(Base):
    """ORM-модель платежа (таблица `payments`).

    Attributes:
        id: уникальный идентификатор платежа.
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        payment_metadata: произвольная дополнительная информация.
        status: текущий статус платежа.
        idempotency_key: уникальный ключ для защиты от дублей.
        webhook_url: адрес для уведомления о результате.
        created_at: дата и время создания платежа; проставляется базой данных.
        processed_at: дата и время обработки платежа.
    """

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, Amount.MAX_SCALE))
    currency: Mapped[Currency] = mapped_column(
        Enum(
            Currency,
            name="currency",
            native_enum=False,
            create_constraint=True,
            length=3,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    description: Mapped[str] = mapped_column(String(Description.MAX_LENGTH))
    payment_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="status",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=lambda e: [m.value for m in e],
        ),
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(IdempotencyKey.MAX_LENGTH), unique=True)
    webhook_url: Mapped[str] = mapped_column(String(WebhookUrl.MAX_LENGTH))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @classmethod
    def from_entity(cls, payment: Payment) -> Self:
        """Создать ORM-модель из доменной сущности.

        Дата создания переносится только у уже сохранённого платежа; для
        нового её проставит база данных.

        Args:
            payment: доменная сущность платежа.

        Returns:
            ORM-модель с данными платежа.
        """
        model = cls(
            id=payment.id,
            amount=Decimal(payment.amount),
            currency=payment.currency,
            description=str(payment.description),
            payment_metadata=dict(payment.metadata),
            status=payment.status,
            idempotency_key=str(payment.idempotency_key),
            webhook_url=str(payment.webhook_url),
            processed_at=payment.processed_at,
        )
        if payment.created_at is not None:
            model.created_at = payment.created_at
        return model

    def to_entity(self) -> Payment:
        """Преобразовать ORM-модель в доменную сущность.

        Returns:
            Доменная сущность платежа.

        Raises:
            ValueObjectValidationError: данные в БД не проходят
                валидацию value objects.
        """
        return Payment(
            id=self.id,
            amount=Amount(self.amount),
            currency=self.currency,
            description=Description(self.description),
            metadata=dict(self.payment_metadata),
            status=self.status,
            idempotency_key=IdempotencyKey(self.idempotency_key),
            webhook_url=WebhookUrl(self.webhook_url),
            created_at=self.created_at,
            processed_at=self.processed_at,
        )
