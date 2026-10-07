from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MessageDTO:
    """Базовый класс исходящих сообщений брокера."""
