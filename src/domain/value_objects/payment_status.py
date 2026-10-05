from enum import StrEnum


class PaymentStatus(StrEnum):
    """Статус платежа.

    Attributes:
        PENDING: платёж создан и ожидает обработки.
        SUCCEEDED: платёж успешно обработан.
        FAILED: обработка платежа завершилась ошибкой.
    """

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
