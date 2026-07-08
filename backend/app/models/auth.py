"""Authentication-related models."""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.core.rbac import Role


class TokenResponse(BaseModel):
    """Token response from Keycloak."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    refresh_expires_in: Optional[int] = None


class UserInfoResponse(BaseModel):
    """Current user information."""
    
    user_id: str
    email: EmailStr
    username: str
    name: Optional[str] = None
    roles: List[Role]
    permissions: List[str]