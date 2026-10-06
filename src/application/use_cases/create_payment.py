from src.application.dto import CreatePaymentDTO, PaymentCreatedMessage, PaymentDTO
from src.application.interfaces import OutboxRepository, PaymentRepository, UnitOfWork
from src.config import Settings
from src.domain.entities import Payment
from src.domain.value_objects import Amount, Description, IdempotencyKey, WebhookUrl


class CreatePaymentUseCase:
    """Сценарий создания платежа.

    Сохраняет платёж и сообщение outbox в одной транзакции; повторный
    запрос с тем же ключом идемпотентности возвращает уже созданный платёж.
    """

    def __init__(self, uow: UnitOfWork, settings: Settings) -> None:
        """Инициализация сценария.

        Args:
            uow: Unit of Work с репозиториями `payments` и `outbox`.
            settings: настройки приложения; из них берётся очередь новых платежей.
        """
        self._uow = uow
        self._queue = settings.rabbit.queue

    async def execute(self, data: CreatePaymentDTO) -> PaymentDTO:
        """Создать платёж и поставить его в очередь на обработку.

        Args:
            data: данные нового платежа.

        Returns:
            Созданный платёж либо существующий, если платёж с таким ключом
            идемпотентности уже был создан.

        Raises:
            ValueObjectValidationError: данные платежа не прошли валидацию.
            PaymentAlreadyExistsError: платёж с таким ключом идемпотентности
                был создан параллельным запросом.
        """
        idempotency_key = IdempotencyKey(data.idempotency_key)

        async with self._uow as uow:
            payments: PaymentRepository = uow.repository("payments")
            outbox: OutboxRepository = uow.repository("outbox")

            existing = await payments.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return self._to_dto(existing)

            payment = await payments.add(
                Payment.create(
                    amount=Amount(data.amount),
                    currency=data.currency,
                    description=Description(data.description),
                    idempotency_key=idempotency_key,
                    webhook_url=WebhookUrl(data.webhook_url),
                    metadata=data.metadata,
                )
            )
            await outbox.add(
                payment.id, self._queue, PaymentCreatedMessage(payment_id=str(payment.id))
            )

            return self._to_dto(payment)

    @staticmethod
    def _to_dto(payment: Payment) -> PaymentDTO:
        """Преобразовать сохранённый платёж в DTO.

        Args:
            payment: сохранённый платёж.

        Returns:
            DTO с идентификатором, статусом и датой создания платежа.
        """
        return PaymentDTO(id=payment.id, status=payment.status, created_at=payment.created_at)
