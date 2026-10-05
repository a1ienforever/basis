from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.presentation import dependencies as deps
from src.web_server import create_app
from tests.fakes import FakeEventPublisher, FakeUnitOfWork


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def app(uow: FakeUnitOfWork, publisher: FakeEventPublisher) -> FastAPI:
    """Real app with infrastructure replaced by in-memory fakes (no Postgres/RabbitMQ needed)."""
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
