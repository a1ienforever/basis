from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import Settings, get_settings
from src.container import create_container
from src.infrastructure.logging import setup_logging
from src.presentation.http.api import setup_routers
from src.presentation.http.api.exception_handlers import register_exception_handlers


def create_app(settings: Settings | None = None) -> FastAPI:
    """Создать HTTP-приложение FastAPI.

    Args:
        settings: настройки приложения; по умолчанию берутся из окружения.

    Returns:
        Сконфигурированное приложение FastAPI.
    """
    settings = settings or get_settings()
    container = create_container(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Освободить ресурсы при остановке."""
        try:
            yield
        finally:
            await container.http_client.aclose()
            await container.engine.dispose()

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    setup_routers(app)
    register_exception_handlers(app)
    app.dependency_overrides.update(container.providers)

    return app


setup_logging(get_settings().log)
app = create_app()
