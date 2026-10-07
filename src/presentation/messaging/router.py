from typing import Annotated
from uuid import UUID

from faststream import AckPolicy, Depends
from faststream.rabbit import RabbitExchange, RabbitMessage, RabbitQueue, RabbitRouter

from src.application.use_cases import ProcessPaymentUseCase
from src.presentation.messaging.dependencies import get_process_payment_use_case
from src.presentation.messaging.schemas import PaymentCreatedBody


def create_router(queue: RabbitQueue, exchange: RabbitExchange) -> RabbitRouter:
    """Создать роутер с подписчиком на очередь новых платежей.

    Args:
        queue: очередь новых платежей с настроенным dead letter exchange.
        exchange: exchange платежей.

    Returns:
        Роутер подписчиков RabbitMQ.
    """
    router = RabbitRouter()

    @router.subscriber(queue, exchange, ack_policy=AckPolicy.REJECT_ON_ERROR)
    async def process_payment(
        body: PaymentCreatedBody,
        message: RabbitMessage,
        use_case: Annotated[ProcessPaymentUseCase, Depends(get_process_payment_use_case)],
    ) -> None:
        """Обработать новый платёж.

        Args:
            body: тело сообщения с идентификатором платежа.
            message: входящее сообщение; его идентификатор служит ключом inbox.
            use_case: сценарий обработки платежа.
        """
        await use_case.execute(UUID(message.message_id), body.payment_id)

    return router
