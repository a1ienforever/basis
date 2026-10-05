from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import DomainError

STATUS_CODES: dict[type[DomainError], int] = {}


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = STATUS_CODES.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
