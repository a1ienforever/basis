from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.presentation import dependencies as deps
from src.web_server import create_app
from tests.fakes import (
    FakeEventPublisher,
    FakeOutboxRepository,
    FakePaymentRepository,
    FakeUnitOfWork,
)


@pytest.fixture
def uow() -> FakeUnitOfWork:
    """In-memory UoW с репозиториями платежей и outbox."""
    return FakeUnitOfWork({"payments": FakePaymentRepository(), "outbox": FakeOutboxRepository()})


@pytest.fixture
def publisher() -> FakeEventPublisher:
    """In-memory издатель событий."""
    return FakeEventPublisher()


@pytest.fixture
def app(uow: FakeUnitOfWork, publisher: FakeEventPublisher) -> FastAPI:
    """Реальное приложение с инфраструктурой, заменённой in-memory фейками."""
    app = create_app()
    app.dependency_overrides.update(
        {
            deps.get_uow: lambda: uow,
            deps.get_event_publisher: lambda: publisher,
        }
    )
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент, обращающийся к приложению напрямую через ASGI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
