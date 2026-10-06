from dataclasses import dataclass

from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from src.config import RabbitSettings


@dataclass(frozen=True, slots=True)
class PaymentsTopology:
    """Топология RabbitMQ для платежей.

    Attributes:
        exchange: exchange платежей; он же служит dead letter exchange.
        queue: очередь новых платежей.
        dlq: очередь «мёртвых» платежей.
    """

    exchange: RabbitExchange
    queue: RabbitQueue
    dlq: RabbitQueue


def create_topology(settings: RabbitSettings) -> PaymentsTopology:
    """Описать exchange платежей и привязанные к нему очереди.

    Args:
        settings: настройки RabbitMQ с именами exchange и очередей.

    Returns:
        Топология платежей; в брокере она создаётся вызовом `declare_topology`.
    """
    exchange = RabbitExchange(settings.exchange, type=ExchangeType.DIRECT)
    dlq = RabbitQueue(settings.dlq)
    queue = RabbitQueue(
        settings.queue,
        arguments={
            "x-dead-letter-exchange": settings.exchange,
            "x-dead-letter-routing-key": settings.dlq,
        },
    )

    return PaymentsTopology(exchange=exchange, queue=queue, dlq=dlq)


async def declare_topology(broker: RabbitBroker, topology: PaymentsTopology) -> None:
    """Объявить exchange и очереди в RabbitMQ и привязать очереди к exchange.

    Ключ привязки каждой очереди совпадает с её именем.

    Args:
        broker: запущенный брокер RabbitMQ.
        topology: топология платежей.
    """
    exchange = await broker.declare_exchange(topology.exchange)

    for queue in (topology.dlq, topology.queue):
        declared = await broker.declare_queue(queue)
        await declared.bind(exchange, routing_key=queue.routing())
