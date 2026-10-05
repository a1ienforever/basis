class DomainError(Exception):
    """Базовый класс всех доменных ошибок."""


class ValueObjectValidationError(DomainError):
    """Базовый класс ошибок валидации value objects."""


class InvalidAmountError(ValueObjectValidationError):
    """Сумма платежа не прошла валидацию.

    Attributes:
        value: исходное значение, из которого пытались создать сумму.
    """

    def __init__(self, value: object) -> None:
        """Инициализация ошибки.

        Args:
            value: исходное значение, не прошедшее валидацию.
        """
        super().__init__(
            f"Invalid amount {value!r}: must be a positive number with at most 2 decimal places"
        )
        self.value = value


class InvalidDescriptionError(ValueObjectValidationError):
    """Описание платежа не прошло валидацию."""

    def __init__(self, max_length: int) -> None:
        """Инициализация ошибки.

        Args:
            max_length: максимально допустимая длина описания.
        """
        super().__init__(f"Invalid description: must be at most {max_length} characters")


class InvalidIdempotencyKeyError(ValueObjectValidationError):
    """Ключ идемпотентности не прошёл валидацию."""

    def __init__(self, max_length: int) -> None:
        """Инициализация ошибки.

        Args:
            max_length: максимально допустимая длина ключа.
        """
        super().__init__(
            "Invalid idempotency key: must be non-empty, without whitespace "
            f"and at most {max_length} characters"
        )


class InvalidWebhookUrlError(ValueObjectValidationError):
    """Webhook URL не прошёл валидацию.

    Attributes:
        value: исходное значение, из которого пытались создать URL.
    """

    def __init__(self, value: object) -> None:
        """Инициализация ошибки.

        Args:
            value: исходное значение, не прошедшее валидацию.
        """
        super().__init__(f"Invalid webhook URL {value!r}: must be an absolute http(s) URL")
        self.value = value


class PaymentAlreadyProcessedError(DomainError):
    """Попытка повторно обработать уже обработанный платёж.

    Attributes:
        payment_id: идентификатор платежа.
        status: текущий статус платежа.
    """

    def __init__(self, payment_id: object, status: str) -> None:
        """Инициализация ошибки.

        Args:
            payment_id: идентификатор платежа.
            status: текущий статус платежа.
        """
        super().__init__(f"Payment '{payment_id}' is already processed with status '{status}'")
        self.payment_id = payment_id
        self.status = status
