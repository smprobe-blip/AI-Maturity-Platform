"""FastAPI dependencies for authentication and authorization."""

from typing import List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppException
from app.integrations.keycloak_client import KeycloakClient, VALID_ROLES

security_scheme = HTTPBearer(auto_error=False)
keycloak_client = KeycloakClient()


class AuthUser:
    """Authenticated user context."""

    def __init__(self, user_id: str, email: str, roles: List[str], token_payload: dict):
        self.user_id = user_id
        self.email = email
        self.roles = roles
        self.token_payload = token_payload

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, roles: List[str]) -> bool:
        return bool(set(self.roles) & set(roles))

    @property
    def is_super_admin(self) -> bool:
        return "super_admin" in self.roles


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> AuthUser:
    """Dependency: extract and verify current user from JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # In development mode, allow a mock token
    if token == "dev-token":
        return AuthUser(
            user_id="dev-user-001",
            email="dev@localhost",
            roles=["super_admin"],
            token_payload={"sub": "dev-user-001"},
        )

    # Verify token with Keycloak
    payload = await keycloak_client.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub", "")
    email = payload.get("email", payload.get("preferred_username", ""))
    roles = await keycloak_client.get_user_roles(payload)

    return AuthUser(
        user_id=user_id,
        email=email,
        roles=roles,
        token_payload=payload,
    )


class RequireRole:
    """Dependency factory: require specific role(s)."""

    def __init__(self, *required_roles: str):
        self.required_roles = list(required_roles)

    async def __call__(self, user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.is_super_admin:
            return user

        if not user.has_any_role(self.required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(self.required_roles)}",
            )

        return user


# Pre-built role dependencies
require_admin = RequireRole("super_admin")
require_facilitator = RequireRole("super_admin", "facilitator")
require_analyst = RequireRole("super_admin", "analyst", "facilitator")
require_sales = RequireRole("super_admin", "sales", "facilitator")
require_auditor = RequireRole("super_admin", "auditor", "analyst", "facilitator")