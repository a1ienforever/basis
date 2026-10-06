from typing import Annotated

from faststream import Depends

from src.application.interfaces import PaymentGateway, UnitOfWork, WebhookSender
from src.application.use_cases import ProcessPaymentUseCase
from src.config import Settings, get_settings
from src.presentation import dependencies as deps


def get_process_payment_use_case(
    uow: Annotated[UnitOfWork, Depends(deps.get_uow)],
    gateway: Annotated[PaymentGateway, Depends(deps.get_payment_gateway)],
    webhooks: Annotated[WebhookSender, Depends(deps.get_webhook_sender)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProcessPaymentUseCase:
    """Собрать сценарий обработки платежа."""
    return ProcessPaymentUseCase(uow, gateway, webhooks, settings)
