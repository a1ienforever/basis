from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import DomainError, PaymentAlreadyExistsError, PaymentNotFoundError

STATUS_CODES: dict[type[DomainError], int] = {
    PaymentAlreadyExistsError: status.HTTP_409_CONFLICT,
    PaymentNotFoundError: status.HTTP_404_NOT_FOUND,
}


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Преобразовать доменную ошибку в HTTP-ответ.

    Код ответа берётся из `STATUS_CODES`, по умолчанию — 400.

    Args:
        request: входящий HTTP-запрос.
        exc: доменная ошибка.

    Returns:
        JSON-ответ с текстом ошибки в поле `detail`.
    """
    status_code = STATUS_CODES.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    """Зарегистрировать обработчики исключений в приложении.

    Args:
        app: приложение FastAPI.
    """
    app.add_exception_handler(DomainError, domain_error_handler)
