from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.config import AuthSettings, get_settings
from src.presentation import dependencies as deps
from src.web_server import create_app
from tests.fakes import (
    FakeInboxRepository,
    FakeOutboxRepository,
    FakePaymentRepository,
    FakeUnitOfWork,
)

TEST_API_KEY = "test-key"


@pytest.fixture
def uow() -> FakeUnitOfWork:
    """In-memory UoW с репозиториями платежей, outbox и inbox."""
    return FakeUnitOfWork(
        {
            "payments": FakePaymentRepository(),
            "outbox": FakeOutboxRepository(),
            "inbox": FakeInboxRepository(),
        }
    )


@pytest.fixture
def app(uow: FakeUnitOfWork) -> FastAPI:
    """Реальное приложение с инфраструктурой, заменённой in-memory фейками."""
    app = create_app()
    settings = get_settings().model_copy(update={"auth": AuthSettings(api_key=TEST_API_KEY)})
    app.dependency_overrides.update(
        {
            deps.get_uow: lambda: uow,
            get_settings: lambda: settings,
        }
    )
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент, обращающийся к приложению напрямую через ASGI с валидным API-ключом."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": TEST_API_KEY},
    ) as client:
        yield client


@pytest.fixture
async def anonymous_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент без API-ключа."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
