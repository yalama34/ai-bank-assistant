from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings

settings = Settings()
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    """
    Проверяет API ключ из заголовка Authorization (Bearer token) или X-API-Key.
    
    Args:
        authorization: Bearer token из заголовка Authorization (опционально)
        x_api_key: API ключ из заголовка X-API-Key
        
    Raises:
        HTTPException: Если ключ отсутствует или неверный
    """
    expected_api_key = settings.API_KEY.get_secret_value()
    
    # Если API_KEY не настроен, пропускаем проверку (для разработки)
    if not expected_api_key:
        return
    
    # Проверяем X-API-Key заголовок (приоритет)
    if x_api_key:
        if x_api_key != expected_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return
    
    # Проверяем Bearer token из Authorization заголовка
    if authorization:
        if authorization.credentials != expected_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return
    
    # Если ни один ключ не предоставлен
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key required. Provide either X-API-Key header or Authorization Bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )

