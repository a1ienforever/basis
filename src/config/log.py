from pydantic import BaseModel


class LogSettings(BaseModel):
    """Настройки логирования.

    Attributes:
        level: минимальный уровень логирования.
        format: формат строки лога.
        datefmt: формат даты и времени в строке лога.
    """

    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
