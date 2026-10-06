from pydantic import BaseModel


class AuthSettings(BaseModel):
    """Настройки аутентификации HTTP API.

    Attributes:
        api_key: статический ключ, ожидаемый в заголовке `X-API-Key`; пустое значение
            отклоняет все запросы к защищённым эндпоинтам.
    """

    api_key: str = ""
