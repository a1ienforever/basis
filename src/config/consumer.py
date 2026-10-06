from pydantic import BaseModel


class ConsumerSettings(BaseModel):
    """Настройки потребителя, обрабатывающего новые платежи.

    Attributes:
        max_attempts: число попыток обработки сообщения, после которого
            оно отправляется в очередь «мёртвых» платежей.
        retry_delay: пауза в секундах перед второй попыткой; перед каждой
            следующей она удваивается.
        webhook_timeout: время ожидания ответа на webhook в секундах.
    """

    max_attempts: int = 3
    retry_delay: float = 1.0
    webhook_timeout: float = 5.0
