from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class OutboxStatus(StrEnum):
    """Статус сообщения outbox.

    Attributes:
        PENDING: сообщение ожидает отправки в брокер.
        PUBLISHED: сообщение отправлено в брокер.
        FAILED: отправить сообщение не удалось.
    """

    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


class OutboxMessageModel(Base):
    """ORM-модель сообщения outbox.

    Attributes:
        id: уникальный идентификатор сообщения.
        aggregate_id: идентификатор агрегата, к которому относится событие.
        event_type: тип события.
        payload: тело события.
        status: текущий статус сообщения.
        attempts: количество попыток отправки.
        error: текст ошибки последней неудачной попытки;
            `None`, если ошибок не было.
        created_at: дата и время создания сообщения; проставляется базой данных.
        published_at: дата и время отправки сообщения в брокер;
            `None`, пока сообщение не отправлено.
    """

    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    aggregate_id: Mapped[UUID] = mapped_column(Uuid)
    event_type: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[OutboxStatus] = mapped_column(
        Enum(
            OutboxStatus,
            name="status",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OutboxStatus.PENDING,
    )
    attempts: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
