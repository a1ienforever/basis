import logging

from faststream.rabbit import Channel, RabbitBroker

from src.config import RabbitSettings

logger = logging.getLogger("broker.rabbit")


def create_broker(settings: RabbitSettings) -> RabbitBroker:
    """Создать брокер RabbitMQ.

    Args:
        settings: настройки подключения к RabbitMQ.

    Returns:
        Брокер FastStream; подключение устанавливается при его запуске.
        Канал работает с publisher confirms и возбуждает исключение,
        когда брокер возвращает немаршрутизируемое сообщение.
    """
    return RabbitBroker(
        settings.url,
        logger=logger,
        default_channel=Channel(publisher_confirms=True, on_return_raises=True),
    )
