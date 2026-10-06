from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from src.application.dto import CreatePaymentDTO
from src.application.use_cases import CreatePaymentUseCase, GetPaymentUseCase
from src.presentation.http.api.v1.schemas import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentResponse,
)
from src.presentation.http.dependencies import (
    get_create_payment_use_case,
    get_payment_use_case,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    body: CreatePaymentRequest,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    use_case: Annotated[CreatePaymentUseCase, Depends(get_create_payment_use_case)],
) -> CreatePaymentResponse:
    """Принять платёж в обработку.

    Повторный запрос с тем же ключом идемпотентности возвращает уже
    созданный платёж.

    Args:
        body: данные платежа.
        idempotency_key: ключ идемпотентности из заголовка `Idempotency-Key`.
        use_case: сценарий создания платежа.

    Returns:
        Идентификатор, статус и дата создания платежа.
    """
    payment = await use_case.execute(
        CreatePaymentDTO(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            metadata=body.metadata,
            webhook_url=body.webhook_url,
            idempotency_key=idempotency_key,
        )
    )
    return CreatePaymentResponse(
        payment_id=payment.id, status=payment.status, created_at=payment.created_at
    )


@router.get("/{payment_id}")
async def get_payment(
    payment_id: UUID,
    use_case: Annotated[GetPaymentUseCase, Depends(get_payment_use_case)],
) -> PaymentResponse:
    """Получить детальную информацию о платеже.

    Args:
        payment_id: идентификатор платежа.
        use_case: сценарий получения информации о платеже.

    Returns:
        Детальная информация о платеже.
    """
    payment = await use_case.execute(payment_id)
    return PaymentResponse(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=payment.metadata,
        status=payment.status,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )
