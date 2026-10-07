import asyncio
import logging
import random

from src.application.interfaces import PaymentGateway
from src.config import GatewaySettings
from src.domain.entities import Payment

logger = logging.getLogger(__name__)

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"


class EmulatedPaymentGateway(PaymentGateway):
    """Эмулятор платёжного шлюза: случайная задержка и случайный результат.

    Реального запроса не делает: заголовки, которые получил бы шлюз,
    включая `Idempotency-Key` платежа, пишутся в журнал.
    """

    def __init__(self, settings: GatewaySettings, rng: random.Random | None = None) -> None:
        """Инициализация эмулятора.

        Args:
            settings: настройки задержки и доли успешных платежей.
            rng: генератор случайных чисел; по умолчанию создаётся новый.
        """
        self._settings = settings
        self._rng = rng or random.Random()

    async def charge(self, payment: Payment) -> bool:
        """Провести платёж.

        Ждёт случайное время от `min_delay` до `max_delay` секунд, не глядя
        на сумму и валюту. В журнал пишется заголовок с ключом идемпотентности
        платежа — тем, по которому реальный шлюз отбросил бы повторный запрос.

        Args:
            payment: платёж, ожидающий обработки.

        Returns:
            `True` с вероятностью `success_rate`, иначе `False`.
        """
        headers = {IDEMPOTENCY_KEY_HEADER: str(payment.idempotency_key)}
        logger.debug("Шлюз: запрос на платёж %s с заголовками %s", payment.id, headers)
        await asyncio.sleep(self._rng.uniform(self._settings.min_delay, self._settings.max_delay))
        return self._rng.random() < self._settings.success_rate
