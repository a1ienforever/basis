from dataclasses import replace
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID

from src.application.dto import MessageDTO
from src.application.interfaces import UnitOfWork
from src.domain.entities import Payment
from src.domain.exceptions import PaymentAlreadyExistsError
from src.domain.value_objects import IdempotencyKey


class FakePaymentRepository:
    """In-memory репозиторий платежей для тестов.

    Attributes:
        payments: сохранённые платежи по ключу идемпотентности.
    """

    def __init__(self) -> None:
        """Инициализация репозитория."""
        self.payments: dict[str, Payment] = {}

    async def get_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment | None:
        """Найти платёж по ключу идемпотентности.

        Args:
            idempotency_key: ключ идемпотентности платежа.

        Returns:
            Платёж или `None`, если платежа с таким ключом нет.
        """
        return self.payments.get(idempotency_key)

    async def add(self, payment: Payment) -> Payment:
        """Сохранить платёж, проставив дату создания.

        Args:
            payment: платёж для сохранения.

        Returns:
            Сохранённый платёж с датой создания.

        Raises:
            PaymentAlreadyExistsError: платёж с таким ключом идемпотентности
                уже существует.
        """
        if payment.idempotency_key in self.payments:
            raise PaymentAlreadyExistsError(payment.idempotency_key)
        saved = replace(payment, created_at=datetime.now(UTC))
        self.payments[saved.idempotency_key] = saved
        return saved


class FakeOutboxRepository:
    """In-memory репозиторий outbox для тестов.

    Attributes:
        messages: сохранённые сообщения с идентификаторами их агрегатов и очередями.
    """

    def __init__(self) -> None:
        """Инициализация репозитория."""
        self.messages: list[tuple[UUID, str, MessageDTO]] = []

    async def add(self, aggregate_id: UUID, queue: str, message: MessageDTO) -> None:
        """Сохранить сообщение в памяти.

        Args:
            aggregate_id: идентификатор агрегата, к которому относится сообщение.
            queue: имя очереди, в которую сообщение будет опубликовано.
            message: сообщение для отправки.
        """
        self.messages.append((aggregate_id, queue, message))


class FakeUnitOfWork(UnitOfWork):
    """In-memory реализация UoW для тестов.

    Attributes:
        repositories: репозитории, доступные по имени.
        committed: был ли вызван коммит.
    """

    def __init__(self, repositories: dict[str, Any] | None = None) -> None:
        """Инициализация UoW.

        Args:
            repositories: репозитории, доступные по имени.
        """
        self.repositories = repositories or {}
        self.committed = False

    async def __aenter__(self) -> Self:
        """Войти в контекст.

        Returns:
            Текущий экземпляр UoW.
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Выйти из контекста: зафиксировать изменения, если не было ошибки.

        Args:
            exc_type: тип исключения, если оно возникло в контексте.
            exc_val: экземпляр исключения, если оно возникло в контексте.
            exc_tb: трассировка исключения, если оно возникло в контексте.
        """
        if exc_type is None:
            await self.commit()

    async def commit(self) -> None:
        """Отметить, что транзакция зафиксирована."""
        self.committed = True

    async def rollback(self) -> None:
        """Откатить транзакцию (ничего не делает)."""
        return None

    def repository(self, name: str) -> Any:
        """Получить репозиторий по имени.

        Args:
            name: имя репозитория.

        Returns:
            Экземпляр репозитория.
        """
        return self.repositories[name]


class FakeEventPublisher:
    """Издатель событий для тестов: накапливает сообщения в памяти.

    Attributes:
        messages: опубликованные сообщения в порядке публикации.
    """

    def __init__(self) -> None:
        """Инициализация издателя."""
        self.messages: list[MessageDTO] = []

    async def publish(self, message: MessageDTO) -> None:
        """Сохранить сообщение в списке опубликованных.

        Args:
            message: сообщение для публикации.
        """
        self.messages.append(message)
