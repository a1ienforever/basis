from typing import Self

from src.domain.exceptions import InvalidDescriptionError


class Description(str):
    """Описание платежа в свободной форме.

    Attributes:
        MAX_LENGTH: максимальная длина описания в символах.
    """

    __slots__ = ()

    MAX_LENGTH = 255

    def __new__(cls, value: str) -> Self:
        """Создать описание с валидацией значения.

        Args:
            value: текст описания; пустая строка допустима.

        Returns:
            Провалидированное описание.

        Raises:
            InvalidDescriptionError: значение не является строкой
                или длиннее `MAX_LENGTH` символов.
        """
        if not isinstance(value, str) or len(value) > cls.MAX_LENGTH:
            raise InvalidDescriptionError(cls.MAX_LENGTH)
        return super().__new__(cls, value)
