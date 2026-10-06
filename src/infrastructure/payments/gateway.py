import asyncio
import random

from src.application.interfaces import PaymentGateway
from src.config import GatewaySettings
from src.domain.entities import Payment


class EmulatedPaymentGateway(PaymentGateway):
    """Эмулятор платёжного шлюза: случайная задержка и случайный результат."""

    def __init__(self, settings: GatewaySettings, rng: random.Random | None = None) -> None:
        """Инициализация эмулятора.

        Args:
            settings: настройки задержки и доли успешных платежей.
            rng: генератор случайных чисел; по умолчанию создаётся новый.
        """
        self._settings = settings
        self._rng = rng or random.Random()

    async def charge(self, payment: Payment) -> bool:
        """Эмулировать проведение платежа.

        Ждёт случайное время от `min_delay` до `max_delay` секунд.

        Args:
            payment: платёж, ожидающий обработки.

        Returns:
            `True` с вероятностью `success_rate`, иначе `False`.
        """
        await asyncio.sleep(self._rng.uniform(self._settings.min_delay, self._settings.max_delay))
        return self._rng.random() < self._settings.success_rate
