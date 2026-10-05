from typing import Self
from urllib.parse import urlsplit

from src.domain.exceptions import InvalidWebhookUrlError


class WebhookUrl(str):
    """Абсолютный http(s) URL для уведомления о результате платежа.

    Attributes:
        MAX_LENGTH: максимальная длина URL в символах.
        ALLOWED_SCHEMES: допустимые схемы URL.
        MIN_PORT: минимальный допустимый номер порта.
        MAX_PORT: максимальный допустимый номер порта.
    """

    __slots__ = ()

    MAX_LENGTH = 2048
    ALLOWED_SCHEMES = frozenset({"http", "https"})
    MIN_PORT = 1
    MAX_PORT = 65535

    def __new__(cls, value: str) -> Self:
        """Создать webhook URL с валидацией значения.

        Args:
            value: адрес, на который отправляется уведомление.

        Returns:
            Провалидированный webhook URL.

        Raises:
            InvalidWebhookUrlError: значение не является строкой, длиннее
                `MAX_LENGTH` символов, содержит пробельные символы, имеет схему
                не из `ALLOWED_SCHEMES`, не содержит хоста или содержит порт,
                который не является числом от `MIN_PORT` до `MAX_PORT`.
        """
        if (
            not isinstance(value, str)
            or len(value) > cls.MAX_LENGTH
            or any(char.isspace() for char in value)
        ):
            raise InvalidWebhookUrlError(value)

        try:
            parts = urlsplit(value)
            port = parts.port
        except ValueError as exc:
            raise InvalidWebhookUrlError(value) from exc

        if parts.scheme not in cls.ALLOWED_SCHEMES or not parts.hostname:
            raise InvalidWebhookUrlError(value)
        if port is not None and not cls.MIN_PORT <= port <= cls.MAX_PORT:
            raise InvalidWebhookUrlError(value)
        return super().__new__(cls, value)
