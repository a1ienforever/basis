from fastapi import APIRouter, Depends, status

from src.presentation.http.api.v1 import payments
from src.presentation.http.security import verify_api_key

v1_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неверный или отсутствующий API-ключ"}
    },
)
v1_router.include_router(payments.router)
