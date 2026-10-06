from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Payment
from src.domain.exceptions import PaymentAlreadyExistsError
from src.domain.value_objects import IdempotencyKey
from src.infrastructure.database.models import PaymentModel


class SQLAlchemyPaymentRepository:
    """Репозиторий платежей на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: сессия SQLAlchemy текущей единицы работы.
        """
        self._session = session

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Найти платёж по идентификатору.

        Args:
            payment_id: идентификатор платежа.

        Returns:
            Платёж или `None`, если платежа с таким идентификатором нет.
        """
        model = await self._session.get(PaymentModel, payment_id)
        return model.to_entity() if model is not None else None

    async def get_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment | None:
        """Найти платёж по ключу идемпотентности.

        Args:
            idempotency_key: ключ идемпотентности платежа.

        Returns:
            Платёж или `None`, если платежа с таким ключом нет.
        """
        model = await self._session.scalar(
            select(PaymentModel).where(PaymentModel.idempotency_key == str(idempotency_key))
        )
        return model.to_entity() if model is not None else None

    async def add(self, payment: Payment) -> Payment:
        """Сохранить новый платёж в рамках текущей транзакции.

        Args:
            payment: платёж для сохранения.

        Returns:
            Сохранённый платёж с датой создания, проставленной базой данных.

        Raises:
            PaymentAlreadyExistsError: платёж с таким ключом идемпотентности
                уже существует.
        """
        model = PaymentModel.from_entity(payment)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise PaymentAlreadyExistsError(payment.idempotency_key) from exc
        await self._session.refresh(model)
        return model.to_entity()
