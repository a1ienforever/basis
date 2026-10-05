from logging.config import dictConfig

from src.config import LogSettings

# Логгеры со своими обработчиками и форматтерами; перенаправляются в корневой обработчик.
THIRD_PARTY_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine", "alembic")


def setup_logging(settings: LogSettings) -> None:
    """Настроить логирование приложения.

    Весь вывод, включая сторонние логгеры, идёт в stdout в едином формате.

    Args:
        settings: настройки логирования.
    """
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": settings.format, "datefmt": settings.datefmt},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": settings.level, "handlers": ["console"]},
            "loggers": {name: {"handlers": [], "propagate": True} for name in THIRD_PARTY_LOGGERS},
        }
    )
