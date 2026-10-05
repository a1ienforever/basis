import logging

from faststream.rabbit import RabbitBroker

from src.config import RabbitSettings

logger = logging.getLogger("broker.rabbit")


def create_broker(settings: RabbitSettings) -> RabbitBroker:
    """Создать брокер RabbitMQ.

    Args:
        settings: настройки подключения к RabbitMQ.

    Returns:
        Брокер FastStream; подключение устанавливается при его запуске.
    """
    return RabbitBroker(settings.url, logger=logger)
