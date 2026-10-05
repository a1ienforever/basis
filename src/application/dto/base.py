from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class MessageDTO:
    """Базовый класс исходящих сообщений брокера.

    Attributes:
        queue: имя очереди, в которую публикуется сообщение.
    """

    queue: ClassVar[str]
