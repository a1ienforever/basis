import json

import httpx
import pytest

from src.application.exceptions import WebhookDeliveryError
from src.infrastructure.webhooks.sender import HttpxWebhookSender

URL = "https://example.com/hook"


def make_sender(handler: httpx.MockTransport) -> HttpxWebhookSender:
    return HttpxWebhookSender(httpx.AsyncClient(transport=handler))


async def test_payload_is_posted_as_json() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    await make_sender(httpx.MockTransport(handler)).send(URL, {"status": "succeeded"})

    assert [(r.method, str(r.url)) for r in requests] == [("POST", URL)]
    assert json.loads(requests[0].content) == {"status": "succeeded"}


async def test_error_status_raises_delivery_error() -> None:
    sender = make_sender(httpx.MockTransport(lambda _: httpx.Response(500)))

    with pytest.raises(WebhookDeliveryError):
        await sender.send(URL, {})


async def test_unreachable_receiver_raises_delivery_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with pytest.raises(WebhookDeliveryError, match="connection refused"):
        await make_sender(httpx.MockTransport(handler)).send(URL, {})
