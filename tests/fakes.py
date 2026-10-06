from dataclasses import replace
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID

from src.application.dto import MessageDTO
from src.application.exceptions import InboxMessageAlreadyExistsError
from src.application.interfaces import PaymentGateway, UnitOfWork, WebhookSender
from src.domain.entities import Payment
from src.domain.exceptions import PaymentAlreadyExistsError
from src.domain.value_objects import IdempotencyKey
from src.infrastructure.database.models import InboxMessageModel, OutboxMessageModel, OutboxStatus


class FakePaymentRepository:
    """In-memory репозиторий платежей для тестов.

    Attributes:
        payments: сохранённые платежи по ключу идемпотентности.
    """

    def __init__(self) -> None:
        """Инициализация репозитория."""
        self.payments: dict[str, Payment] = {}

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Найти платёж по идентификатору.

        Args:
            payment_id: идентификатор платежа.

        Returns:
            Платёж или `None`, если платежа с таким идентификатором нет.
        """
        return next((p for p in self.payments.values() if p.id == payment_id), None)

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

    async def update(self, payment: Payment) -> None:
        """Сохранить изменения платежа.

        Args:
            payment: платёж с изменёнными данными.
        """
        self.payments[payment.idempotency_key] = payment


class FakeOutboxRepository:
    """In-memory репозиторий outbox для тестов.

    Attributes:
        messages: сохранённые сообщения с идентификаторами их агрегатов и очередями.
        rows: строки outbox, из которых relay выбирает ожидающие отправки.
    """

    def __init__(self) -> None:
        """Инициализация репозитория."""
        self.messages: list[tuple[UUID, str, MessageDTO]] = []
        self.rows: list[OutboxMessageModel] = []

    async def add(self, aggregate_id: UUID, queue: str, message: MessageDTO) -> None:
        """Сохранить сообщение в памяти.

        Args:
            aggregate_id: идентификатор агрегата, к которому относится сообщение.
            queue: имя очереди, в которую сообщение будет опубликовано.
            message: сообщение для отправки.
        """
        self.messages.append((aggregate_id, queue, message))

    async def lock_pending(self, limit: int) -> list[OutboxMessageModel]:
        """Вернуть ожидающие отправки строки.

        Args:
            limit: максимальное число строк.

        Returns:
            Строки в статусе `pending` в порядке добавления.
        """
        return [row for row in self.rows if row.status is OutboxStatus.PENDING][:limit]


class FakeInboxRepository:
    """In-memory репозиторий inbox для тестов.

    Attributes:
        rows: обработанные сообщения по паре потребителя и идентификатора.
    """

    def __init__(self) -> None:
        """Инициализация репозитория."""
        self.rows: dict[tuple[str, UUID], InboxMessageModel] = {}

    async def create(self, consumer: str, message_id: UUID) -> None:
        """Сохранить сообщение в памяти.

        Args:
            consumer: имя потребителя, обработавшего сообщение.
            message_id: идентификатор сообщения в outbox отправителя.

        Raises:
            InboxMessageAlreadyExistsError: сообщение уже сохранено
                этим потребителем.
        """
        if (consumer, message_id) in self.rows:
            raise InboxMessageAlreadyExistsError(consumer, message_id)
        self.rows[consumer, message_id] = InboxMessageModel(
            consumer=consumer, message_id=message_id, processed_at=datetime.now(UTC)
        )


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


class FakeOutboxPublisher:
    """Издатель outbox для тестов: накапливает сообщения и возбуждает заданные ошибки.

    Attributes:
        published: опубликованные сообщения в порядке публикации.
        errors: ошибки, возбуждаемые по одной на каждый следующий вызов.
    """

    def __init__(self, errors: list[Exception] | None = None) -> None:
        """Инициализация издателя.

        Args:
            errors: ошибки, возбуждаемые по одной на каждый следующий вызов.
        """
        self.published: list[tuple[UUID, str, dict[str, Any]]] = []
        self.errors = list(errors or [])

    async def publish(self, message_id: UUID, routing_key: str, payload: dict[str, Any]) -> None:
        """Сохранить сообщение либо возбудить очередную заданную ошибку.

        Args:
            message_id: идентификатор сообщения.
            routing_key: ключ маршрутизации сообщения.
            payload: тело сообщения.
        """
        if self.errors:
            raise self.errors.pop(0)
        self.published.append((message_id, routing_key, payload))


class FakePaymentGateway(PaymentGateway):
    """Платёжный шлюз для тестов: возвращает заданный результат без задержки.

    Attributes:
        success: результат проведения платежей.
        charged: идентификаторы проведённых платежей в порядке вызовов.
    """

    def __init__(self, success: bool = True) -> None:
        """Инициализация шлюза.

        Args:
            success: результат проведения платежей.
        """
        self.success = success
        self.charged: list[UUID] = []

    async def charge(self, payment: Payment) -> bool:
        """Запомнить платёж и вернуть заданный результат.

        Args:
            payment: платёж, ожидающий обработки.

        Returns:
            Заданный результат проведения платежа.
        """
        self.charged.append(payment.id)
        return self.success


class FakeWebhookSender(WebhookSender):
    """Отправитель webhook для тестов: накапливает уведомления и возбуждает заданные ошибки.

    Attributes:
        sent: доставленные уведомления в порядке отправки.
        errors: ошибки, возбуждаемые по одной на каждый следующий вызов.
        calls: число вызовов, включая неудачные.
    """

    def __init__(self, errors: list[Exception] | None = None) -> None:
        """Инициализация отправителя.

        Args:
            errors: ошибки, возбуждаемые по одной на каждый следующий вызов.
        """
        self.sent: list[tuple[str, dict[str, Any]]] = []
        self.errors = list(errors or [])
        self.calls = 0

    async def send(self, url: str, payload: dict[str, Any]) -> None:
        """Сохранить уведомление либо возбудить очередную заданную ошибку.

        Args:
            url: адрес получателя уведомления.
            payload: тело уведомления.
        """
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        self.sent.append((url, payload))
