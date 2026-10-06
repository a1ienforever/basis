import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime

from src.application.interfaces import UnitOfWork
from src.config import OutboxSettings
from src.infrastructure.database.models import OutboxMessageModel, OutboxStatus
from src.infrastructure.exceptions import BrokerUnavailableError, EventPublishError
from src.infrastructure.messaging.outbox_publisher import RabbitOutboxPublisher

logger = logging.getLogger(__name__)
alert_logger = logging.getLogger("outbox.alert")


class OutboxRelay:
    """Relay, переносящий сообщения из таблицы outbox в брокер."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        publisher: RabbitOutboxPublisher,
        settings: OutboxSettings,
    ) -> None:
        """Инициализация relay.

        Args:
            uow_factory: фабрика Unit of Work с репозиторием `outbox`.
            publisher: издатель сообщений в брокер.
            settings: настройки relay.
        """
        self._uow_factory = uow_factory
        self._publisher = publisher
        self._settings = settings
        self._stopped = asyncio.Event()

    async def run(self) -> None:
        """Публиковать сообщения outbox.

        Если outbox пустой relay ждёт `poll_interval` перед следующей попыткой.
        """
        self._stopped.clear()
        logger.info("Outbox relay: запущен")

        while not self._stopped.is_set():
            try:
                progressed = await self.process_batch()
            except Exception:
                logger.exception("Outbox relay: ошибка обработки пачки")
                progressed = False

            if not progressed:
                await self._wait()

        logger.info("Outbox relay: остановлен")

    def stop(self) -> None:
        """Остановить relay после завершения текущей пачки."""
        self._stopped.set()

    async def process_batch(self) -> bool:
        """Опубликовать одну пачку ожидающих сообщений в одной транзакции.

        Returns:
            `True`, если опубликовано сообщение и брокер доступен.
        """
        published = 0

        async with self._uow_factory() as uow:
            messages: list[OutboxMessageModel] = await uow.repository("outbox").lock_pending(
                self._settings.batch_size
            )

            for message in messages:
                try:
                    await self._publisher.publish(message.id, message.event_type, message.payload)
                except BrokerUnavailableError as exc:
                    logger.warning("Outbox relay: брокер недоступен: %s", exc)
                    return False
                except EventPublishError as exc:
                    self._register_failure(message, exc)
                else:
                    message.status = OutboxStatus.PUBLISHED
                    message.published_at = datetime.now(UTC)
                    message.error = None
                    published += 1

        return published > 0

    def _register_failure(self, message: OutboxMessageModel, exc: EventPublishError) -> None:
        """Учесть неудачную попытку публикации сообщения.

        После `max_attempts` попыток сообщение получает статус `failed`
        и больше не публикуется.

        Args:
            message: сообщение, которое не удалось опубликовать.
            exc: ошибка публикации.
        """
        message.attempts += 1
        message.error = str(exc)

        if message.attempts < self._settings.max_attempts:
            logger.warning(
                "Outbox relay: сообщение %s не опубликовано (попытка %d из %d): %s",
                message.id,
                message.attempts,
                self._settings.max_attempts,
                exc,
            )
            return

        message.status = OutboxStatus.FAILED
        alert_logger.critical(
            "Outbox: сообщение %s (агрегат %s, событие %s) не опубликовано за %d попыток: %s",
            message.id,
            message.aggregate_id,
            message.event_type,
            message.attempts,
            exc,
        )

    async def _wait(self) -> None:
        """Подождать `poll_interval` или до остановки relay."""
        try:
            await asyncio.wait_for(self._stopped.wait(), self._settings.poll_interval)
        except TimeoutError:
            pass
