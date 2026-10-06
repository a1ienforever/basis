from typing import Annotated

from fastapi import Depends

from src.application.interfaces import UnitOfWork
from src.application.use_cases import CreatePaymentUseCase
from src.config import Settings, get_settings
from src.presentation import dependencies as deps


def get_create_payment_use_case(
    uow: Annotated[UnitOfWork, Depends(deps.get_uow)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CreatePaymentUseCase:
    """Собрать сценарий создания платежа."""
    return CreatePaymentUseCase(uow, settings)
