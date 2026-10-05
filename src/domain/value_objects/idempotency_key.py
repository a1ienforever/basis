from typing import Self

from src.domain.exceptions import InvalidIdempotencyKeyError


class IdempotencyKey(str):
    """Ключ идемпотентности, защищающий от создания дублей платежа.

    Attributes:
        MAX_LENGTH: максимальная длина ключа в символах.
    """

    __slots__ = ()

    MAX_LENGTH = 255

    def __new__(cls, value: str) -> Self:
        """Создать ключ идемпотентности с валидацией значения.

        Args:
            value: ключ, переданный клиентом.

        Returns:
            Провалидированный ключ идемпотентности.

        Raises:
            InvalidIdempotencyKeyError: значение не является строкой, пустое,
                содержит пробельные символы или длиннее `MAX_LENGTH` символов.
        """
        if (
            not isinstance(value, str)
            or not value
            or len(value) > cls.MAX_LENGTH
            or any(char.isspace() for char in value)
        ):
            raise InvalidIdempotencyKeyError(cls.MAX_LENGTH)
        return super().__new__(cls, value)
