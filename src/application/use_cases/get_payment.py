from uuid import UUID

from src.application.dto import PaymentDetailsDTO
from src.application.interfaces import PaymentRepository, UnitOfWork
from src.domain.exceptions import PaymentNotFoundError


class GetPaymentUseCase:
    """Сценарий получения информации о платеже."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализация сценария.

        Args:
            uow: Unit of Work с репозиторием `payments`.
        """
        self._uow = uow

    async def execute(self, payment_id: UUID) -> PaymentDetailsDTO:
        """Получить детальную информацию о платеже.

        Args:
            payment_id: идентификатор платежа.

        Returns:
            Детальная информация о платеже.

        Raises:
            PaymentNotFoundError: платежа с таким идентификатором нет.
        """
        async with self._uow as uow:
            payments: PaymentRepository = uow.repository("payments")
            payment = await payments.get_by_id(payment_id)

        if payment is None:
            raise PaymentNotFoundError(payment_id)

        return PaymentDetailsDTO(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            metadata=payment.metadata,
            status=payment.status,
            webhook_url=payment.webhook_url,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
        )
