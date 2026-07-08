"""JWT Authentication and Authorization for Keycloak."""

import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from pydantic import BaseModel
from typing import List, Optional

from app.core.config import settings

logger = structlog.get_logger()

security = HTTPBearer()


class User(BaseModel):
    """User model extracted from JWT token."""
    sub: str
    preferred_username: str
    email: Optional[str] = None
    realm_roles: List[str] = []


# Кэш для JWKS ключей
_jwks_cache = {}


async def get_jwks():
    """Fetch JWKS from Keycloak and cache it."""
    if _jwks_cache:
        return _jwks_cache
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.KEYCLOAK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache.update(response.json())
            return _jwks_cache
    except Exception as e:
        logger.error("jwks_fetch_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Validate JWT token and extract user information."""
    token = credentials.credentials
    
    try:
        # Получаем JWKS ключи
        jwks = await get_jwks()
        
        # Декодируем и проверяем токен
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={
                "verify_aud": False,   # Отключаем проверку audience
                "verify_iss": False,   # Отключаем проверку issuer
                "leeway": 14400,       # 4 часа погрешности для TZ
            }
        )
        
        # Извлекаем данные пользователя
        user = User(
            sub=payload.get("sub", ""),
            preferred_username=payload.get("preferred_username", ""),
            email=payload.get("email"),
            realm_roles=payload.get("realm_roles", []),
        )
        
        logger.info("user_authenticated",
                   username=user.preferred_username,
                   roles=user.realm_roles)
        
        return user
        
    except ExpiredSignatureError:
        logger.error("jwt_expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError as e:
        logger.error("jwt_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except Exception as e:
        logger.error("auth_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


def require_role(required_role: str):
    """Dependency factory to check if user has a specific role."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if required_role not in current_user.realm_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' is required",
            )
        return current_user
    return role_checker
