from enum import StrEnum


class Currency(StrEnum):
    """Валюта платежа.

    Attributes:
        RUB: российский рубль.
        USD: доллар США.
        EUR: евро.
    """

    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
