from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class MessageDTO:
    """Base class for outgoing broker messages; `queue` is the destination queue."""

    queue: ClassVar[str]
