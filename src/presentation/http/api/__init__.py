from fastapi import FastAPI

from src.presentation.http.api import health
from src.presentation.http.api.v1 import v1_router


def setup_routers(app: FastAPI) -> None:
    """Подключить HTTP-роутеры к приложению.

    Args:
        app: приложение FastAPI.
    """
    app.include_router(health.router)
    app.include_router(v1_router)
