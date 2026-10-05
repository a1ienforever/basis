import logging

from faststream.rabbit import RabbitBroker

from src.config import RabbitSettings

logger = logging.getLogger("broker.rabbit")


def create_broker(settings: RabbitSettings) -> RabbitBroker:
    return RabbitBroker(settings.url, logger=logger)
