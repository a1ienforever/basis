from typing import Protocol
from uuid import UUID

from src.domain.entities import Payment
from src.domain.value_objects import IdempotencyKey


class PaymentRepository(Protocol):
    """Интерфейс репозитория платежей."""

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Найти платёж по идентификатору.

        Args:
            payment_id: идентификатор платежа.

        Returns:
            Платёж или `None`, если платежа с таким идентификатором нет.
        """
        ...

    async def get_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment | None:
        """Найти платёж по ключу идемпотентности.

        Args:
            idempotency_key: ключ идемпотентности платежа.

        Returns:
            Платёж или `None`, если платежа с таким ключом нет.
        """
        ...

    async def add(self, payment: Payment) -> Payment:
        """Сохранить новый платёж.

        Args:
            payment: платёж для сохранения.

        Returns:
            Сохранённый платёж с проставленной датой создания.

        Raises:
            PaymentAlreadyExistsError: платёж с таким ключом идемпотентности
                уже существует.
        """
        ...
