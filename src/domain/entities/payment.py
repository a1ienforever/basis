from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4

from src.domain.exceptions import PaymentAlreadyProcessedError
from src.domain.value_objects import (
    Amount,
    Currency,
    Description,
    IdempotencyKey,
    PaymentStatus,
    WebhookUrl,
)


@dataclass(slots=True, kw_only=True)
class Payment:
    """Платёж.

    Attributes:
        id: уникальный идентификатор платежа.
        amount: сумма платежа.
        currency: валюта платежа.
        description: описание платежа.
        idempotency_key: уникальный ключ для защиты от дублей.
        webhook_url: адрес для уведомления о результате.
        status: текущий статус платежа.
        metadata: произвольная дополнительная информация.
        created_at: дата и время создания платежа (UTC); проставляется
            базой данных, `None`, пока платёж не сохранён.
        processed_at: дата и время обработки платежа (UTC);
            `None`, пока платёж не обработан.
    """

    id: UUID
    amount: Amount
    currency: Currency
    description: Description
    idempotency_key: IdempotencyKey
    webhook_url: WebhookUrl
    status: PaymentStatus = PaymentStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    processed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        amount: Amount,
        currency: Currency,
        description: Description,
        idempotency_key: IdempotencyKey,
        webhook_url: WebhookUrl,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        """Создать новый платёж в статусе ожидания обработки.

        Args:
            amount: сумма платежа.
            currency: валюта платежа.
            description: описание платежа.
            idempotency_key: уникальный ключ для защиты от дублей.
            webhook_url: адрес для уведомления о результате.
            metadata: произвольная дополнительная информация.

        Returns:
            Новый платёж со статусом `PaymentStatus.PENDING`.
        """
        return cls(
            id=uuid4(),
            amount=amount,
            currency=currency,
            description=description,
            idempotency_key=idempotency_key,
            webhook_url=webhook_url,
            metadata=dict(metadata or {}),
        )

    def mark_succeeded(self) -> None:
        """Отметить платёж успешно обработанным.

        Raises:
            PaymentAlreadyProcessedError: платёж уже был обработан.
        """
        self._process(PaymentStatus.SUCCEEDED)

    def mark_failed(self) -> None:
        """Отметить платёж обработанным с ошибкой.

        Raises:
            PaymentAlreadyProcessedError: платёж уже был обработан.
        """
        self._process(PaymentStatus.FAILED)

    def _process(self, status: PaymentStatus) -> None:
        """Перевести платёж в итоговый статус и проставить дату обработки.

        Args:
            status: итоговый статус платежа.

        Raises:
            PaymentAlreadyProcessedError: платёж не находится в статусе
                `PaymentStatus.PENDING`.
        """
        if self.status is not PaymentStatus.PENDING:
            raise PaymentAlreadyProcessedError(self.id, self.status)
        self.status = status
        self.processed_at = datetime.now(UTC)
