from decimal import Decimal, InvalidOperation
from typing import Self

from src.domain.exceptions import InvalidAmountError


class Amount(Decimal):
    """Сумма платежа: положительное число с ограниченной точностью.

    Attributes:
        MAX_SCALE: максимальное количество знаков после запятой.
    """

    __slots__ = ()

    MAX_SCALE = 2

    def __new__(cls, value: Decimal | int | str) -> Self:
        """Создать сумму с валидацией значения.

        Args:
            value: исходное значение суммы.

        Returns:
            Провалидированная сумма.

        Raises:
            InvalidAmountError: значение не является числом, не конечно,
                не положительно или содержит больше `MAX_SCALE` знаков после запятой.
        """
        try:
            amount = super().__new__(cls, value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise InvalidAmountError(value) from exc

        if not amount.is_finite() or amount <= 0:
            raise InvalidAmountError(value)
        exponent = amount.as_tuple().exponent
        if not isinstance(exponent, int) or exponent < -cls.MAX_SCALE:
            raise InvalidAmountError(value)
        return amount
