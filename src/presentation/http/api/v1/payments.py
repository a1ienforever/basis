from typing import Annotated

from fastapi import APIRouter, Depends, Header, status

from src.application.dto import CreatePaymentDTO
from src.application.use_cases import CreatePaymentUseCase
from src.presentation.http.api.v1.schemas import CreatePaymentRequest, CreatePaymentResponse
from src.presentation.http.dependencies import get_create_payment_use_case

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
