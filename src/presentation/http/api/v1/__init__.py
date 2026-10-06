from fastapi import APIRouter

from src.presentation.http.api.v1 import payments

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(payments.router)
