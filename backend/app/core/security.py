from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    """
    Dependency для проверки API ключа.
    Если API_KEY не задан в настройках, проверка пропускается (для разработки).
    """
    # Получаем API_KEY из настроек
    api_key_from_config = getattr(settings, "API_KEY", None)
    
    # Если API_KEY не задан в конфиге, пропускаем проверку
    if not api_key_from_config:
        return "dev_mode"
    
    # Если ключ не передан в заголовке
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header."
        )
    
    # Проверяем соответствие ключа
    if api_key != api_key_from_config:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return api_key

