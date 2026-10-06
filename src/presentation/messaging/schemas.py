from uuid import UUID

from pydantic import BaseModel


class PaymentCreatedBody(BaseModel):
    """Тело сообщения о создании платежа, ожидающего обработки.

    Attributes:
        payment_id: идентификатор созданного платежа.
    """

    payment_id: UUID
