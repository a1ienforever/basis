from decimal import Decimal

import pytest

from src.domain.exceptions import (
    InvalidAmountError,
    InvalidDescriptionError,
    InvalidIdempotencyKeyError,
    InvalidWebhookUrlError,
)
from src.domain.value_objects import Amount, Description, IdempotencyKey, WebhookUrl


@pytest.mark.parametrize("value", ["100", "0.01", "99.9", 5, Decimal("1234567.89")])
def test_amount_accepts_valid_values(value: Decimal | int | str) -> None:
    amount = Amount(value)

    assert isinstance(amount, Decimal)
    assert amount == Decimal(value)


@pytest.mark.parametrize(
    "value", ["0", "-1", "0.001", "NaN", "Infinity", "-Infinity", "abc", "", None]
)
def test_amount_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidAmountError):
        Amount(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [
        "https://example.com/hook",
        "http://localhost:8000/payments/callback?source=basis",
        "https://sub.example.com",
        "https://example.com:1/hook",
        "https://example.com:65535/hook",
    ],
)
def test_webhook_url_accepts_valid_values(value: str) -> None:
    url = WebhookUrl(value)

    assert isinstance(url, str)
    assert url == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "example.com/hook",
        "ftp://example.com/hook",
        "https://",
        "https:///hook",
        "https://example.com/ho ok",
        "https://example.com:port/hook",
        "https://example.com:0/hook",
        "https://example.com:65536/hook",
        "https://example.com:-1/hook",
        "https://example.com/" + "a" * WebhookUrl.MAX_LENGTH,
        None,
    ],
)
def test_webhook_url_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidWebhookUrlError):
        WebhookUrl(value)  # type: ignore[arg-type]


def test_idempotency_key_accepts_valid_value() -> None:
    key = IdempotencyKey("order-42:attempt-1")

    assert isinstance(key, str)
    assert key == "order-42:attempt-1"


@pytest.mark.parametrize("value", ["", "with space", "tab\tkey", "k" * 256, None])
def test_idempotency_key_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidIdempotencyKeyError):
        IdempotencyKey(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "Оплата заказа №42", "d" * 255])
def test_description_accepts_valid_values(value: str) -> None:
    assert Description(value) == value


@pytest.mark.parametrize("value", ["d" * 256, None])
def test_description_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidDescriptionError):
        Description(value)  # type: ignore[arg-type]
