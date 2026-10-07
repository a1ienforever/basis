import json
from collections.abc import Callable

import httpx
import pytest

from src.application.exceptions import WebhookDeliveryError
from src.infrastructure.webhooks.sender import HttpxWebhookSender

URL = "https://example.com/hook"


def make_sender(handler: Callable[[httpx.Request], httpx.Response]) -> HttpxWebhookSender:
    return HttpxWebhookSender(httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def unreachable(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


async def test_payload_is_posted_as_json() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    await make_sender(handler).send(URL, {"status": "succeeded"})

    assert [(r.method, str(r.url)) for r in requests] == [("POST", URL)]
    assert json.loads(requests[0].content) == {"status": "succeeded"}


@pytest.mark.parametrize("handler", [lambda _: httpx.Response(500), unreachable])
async def test_failed_delivery_raises_delivery_error(
    handler: Callable[[httpx.Request], httpx.Response],
) -> None:
    with pytest.raises(WebhookDeliveryError):
        await make_sender(handler).send(URL, {})
