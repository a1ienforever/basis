from httpx import AsyncClient

URL = "/api/v1/payments/00000000-0000-0000-0000-000000000000"


async def test_request_without_api_key_is_rejected(anonymous_client: AsyncClient) -> None:
    response = await anonymous_client.get(URL)

    assert response.status_code == 401
    assert "detail" in response.json()


async def test_request_with_wrong_api_key_is_rejected(anonymous_client: AsyncClient) -> None:
    response = await anonymous_client.get(URL, headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
    assert "detail" in response.json()


async def test_health_does_not_require_api_key(anonymous_client: AsyncClient) -> None:
    response = await anonymous_client.get("/health")

    assert response.status_code == 200


async def test_openapi_does_not_require_api_key(anonymous_client: AsyncClient) -> None:
    response = await anonymous_client.get("/openapi.json")

    assert response.status_code == 200
