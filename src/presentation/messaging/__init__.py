from faststream.rabbit import RabbitBroker

from src.presentation.messaging.router import router


def setup_routers(broker: RabbitBroker) -> None:
    """Подключить роутеры подписчиков к брокеру.

    Args:
        broker: брокер RabbitMQ.
    """
    broker.include_router(router)
