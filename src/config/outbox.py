from pydantic import BaseModel


class OutboxSettings(BaseModel):
    """Настройки relay, публикующего сообщения outbox в брокер.

    Attributes:
        batch_size: максимальное число сообщений, обрабатываемых за одну транзакцию.
        poll_interval: пауза в секундах, когда публиковать нечего или брокер недоступен.
        max_attempts: число неудачных попыток, после которого сообщение
            получает статус `failed`.
        publish_timeout: время ожидания подтверждения брокера в секундах.
    """

    batch_size: int = 100
    poll_interval: float = 1.0
    max_attempts: int = 5
    publish_timeout: float = 5.0
