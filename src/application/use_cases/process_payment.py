import asyncio
import logging
from typing import Any
from uuid import UUID

from src.application.interfaces import (
    PaymentGateway,
    PaymentRepository,
    UnitOfWork,
    WebhookSender,
)
from src.application.services import InboxService
from src.config import Settings
from src.domain.entities import Payment
from src.domain.exceptions import DomainError, PaymentNotFoundError
from src.domain.value_objects import PaymentStatus

logger = logging.getLogger(__name__)


class ProcessPaymentUseCase:
    """Сценарий обработки платежа, полученного из очереди.

    Проводит платёж через шлюз, сохраняет итоговый статус и уведомляет
    клиента по webhook. Неудачная попытка повторяется с экспоненциальной
    задержкой; платёж при этом проводится один раз, повторяется только то,
    что не было выполнено.

    Attributes:
        CONSUMER: имя потребителя, под которым сообщения регистрируются в inbox.
    """

    CONSUMER = "payments.process"

    def __init__(
        self,
        uow: UnitOfWork,
        gateway: PaymentGateway,
        webhooks: WebhookSender,
        settings: Settings,
    ) -> None:
        """Инициализация сценария.

        Args:
            uow: Unit of Work с репозиториями `payments` и `inbox`.
            gateway: платёжный шлюз.
            webhooks: отправитель webhook-уведомлений.
            settings: настройки приложения; из них берутся число попыток
                и задержка между ними.
        """
        self._uow = uow
        self._gateway = gateway
        self._webhooks = webhooks
        self._inbox = InboxService()
        self._max_attempts = settings.consumer.max_attempts
        self._retry_delay = settings.consumer.retry_delay

    async def execute(self, message_id: UUID, payment_id: UUID) -> None:
        """Обработать платёж и уведомить клиента о результате.

        Args:
            message_id: идентификатор сообщения в outbox отправителя.
            payment_id: идентификатор платежа.

        Raises:
            DomainError: сообщение не может быть обработано, например платежа
                с таким идентификатором нет; попытки не повторяются.
            Exception: ошибка последней из `max_attempts` попыток.
        """
        for attempt in range(1, self._max_attempts + 1):
            try:
                await self._attempt(message_id, payment_id)
            except DomainError:
                raise
            except Exception as exc:
                if attempt == self._max_attempts:
                    logger.error(
                        "Платёж %s не обработан за %d попыток: %s", payment_id, attempt, exc
                    )
                    raise
                logger.warning(
                    "Платёж %s не обработан (попытка %d из %d): %s",
                    payment_id,
                    attempt,
                    self._max_attempts,
                    exc,
                )
                await asyncio.sleep(self._retry_delay * 2 ** (attempt - 1))
            else:
                return

    async def _attempt(self, message_id: UUID, payment_id: UUID) -> None:
        """Выполнить одну попытку: провести платёж и отправить уведомление.

        Args:
            message_id: идентификатор сообщения в outbox отправителя.
            payment_id: идентификатор платежа.

        Raises:
            PaymentNotFoundError: платежа с таким идентификатором нет.
            WebhookDeliveryError: уведомление не доставлено.
        """
        payment = await self._process(message_id, payment_id)
        await self._webhooks.send(payment.webhook_url, self._to_payload(payment))

    async def _process(self, message_id: UUID, payment_id: UUID) -> Payment:
        """Провести платёж и сохранить его статус, если это ещё не сделано.

        Args:
            message_id: идентификатор сообщения в outbox отправителя.
            payment_id: идентификатор платежа.

        Returns:
            Платёж в итоговом статусе.

        Raises:
            PaymentNotFoundError: платежа с таким идентификатором нет.
        """
        async with self._uow as uow:
            payments: PaymentRepository = uow.repository("payments")

            is_new = await self._inbox.register(uow, self.CONSUMER, message_id)
            payment = await payments.get_by_id(payment_id)
            if payment is None:
                raise PaymentNotFoundError(payment_id)

            if is_new and payment.status is PaymentStatus.PENDING:
                if await self._gateway.charge(payment):
                    payment.mark_succeeded()
                else:
                    payment.mark_failed()
                await payments.update(payment)
                logger.info("Платёж %s обработан со статусом %s", payment.id, payment.status)

            return payment

    @staticmethod
    def _to_payload(payment: Payment) -> dict[str, Any]:
        """Собрать тело webhook-уведомления о результате платежа.

        Args:
            payment: обработанный платёж.

        Returns:
            Данные платежа, пригодные для сериализации в JSON.
        """
        return {
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "amount": str(payment.amount),
            "currency": payment.currency.value,
            "description": str(payment.description),
            "metadata": payment.metadata,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }
