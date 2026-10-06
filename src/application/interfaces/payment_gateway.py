from abc import ABC, abstractmethod

from src.domain.entities import Payment


class PaymentGateway(ABC):
    """Интерфейс платёжного шлюза, проводящего платежи."""

    @abstractmethod
    async def charge(self, payment: Payment) -> bool:
        """Провести платёж.

        Args:
            payment: платёж, ожидающий обработки.

        Returns:
            `True`, если платёж проведён успешно; `False`, если шлюз его отклонил.
        """
        ...
