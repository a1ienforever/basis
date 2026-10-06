from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from src.presentation.messaging.router import create_router


def setup_routers(broker: RabbitBroker, queue: RabbitQueue, exchange: RabbitExchange) -> None:
    """Подключить роутеры подписчиков к брокеру.

    Args:
        broker: брокер RabbitMQ.
        queue: очередь новых платежей.
        exchange: exchange платежей.
    """
    broker.include_router(create_router(queue, exchange))
