import pytest
from httpx import AsyncClient

PAYMENT_URL = "/api/v1/payments/00000000-0000-0000-0000-000000000000"


@pytest.mark.parametrize("headers", [None, {"X-API-Key": "wrong-key"}])
async def test_request_without_valid_api_key_is_rejected(
    anonymous_client: AsyncClient, headers: dict[str, str] | None
) -> None:
    response = await anonymous_client.get(PAYMENT_URL, headers=headers)

    assert response.status_code == 401
    assert "detail" in response.json()


async def test_health_is_public(anonymous_client: AsyncClient) -> None:
    response = await anonymous_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_openapi_is_public(anonymous_client: AsyncClient) -> None:
    assert (await anonymous_client.get("/openapi.json")).status_code == 200
