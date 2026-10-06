from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.config import Settings, get_settings

API_KEY_HEADER = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


async def verify_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Проверить статический API-ключ из заголовка `X-API-Key`.

    Args:
        api_key: ключ из заголовка запроса, если он передан.
        settings: настройки приложения.

    Raises:
        HTTPException: ключ не передан, не совпадает с ожидаемым или не настроен.
    """
    expected = settings.auth.api_key
    if not expected or not api_key or not compare_digest(api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или отсутствующий API-ключ",
        )
