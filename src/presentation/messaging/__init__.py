from faststream.rabbit import RabbitBroker

from src.presentation.messaging.router import router


def setup_routers(broker: RabbitBroker) -> None:
    broker.include_router(router)
