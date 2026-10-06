from pydantic import BaseModel


class GatewaySettings(BaseModel):
    """Настройки эмулятора платёжного шлюза.

    Attributes:
        min_delay: минимальное время обработки платежа в секундах.
        max_delay: максимальное время обработки платежа в секундах.
        success_rate: доля платежей, обрабатываемых успешно, от 0 до 1.
    """

    min_delay: float = 2.0
    max_delay: float = 5.0
    success_rate: float = 0.9
