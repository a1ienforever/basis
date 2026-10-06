from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class InboxMessageModel(Base):
    """ORM-модель сообщения inbox.

    Attributes:
        consumer: имя потребителя, обработавшего сообщение.
        message_id: идентификатор сообщения в outbox отправителя.
        processed_at: дата и время обработки сообщения; проставляется базой данных.
    """

    __tablename__ = "inbox"

    consumer: Mapped[str] = mapped_column(String(255), primary_key=True)
    message_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
