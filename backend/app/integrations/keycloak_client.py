"""Keycloak OIDC client for authentication and RBAC."""

from typing import Any, Dict, List, Optional

import httpx
import structlog
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import IntegrationException

logger = structlog.get_logger()

# Keycloak JWKS cache
_jwks_cache: Optional[Dict[str, Any]] = None

# Valid roles for the platform
VALID_ROLES = [
    "super_admin",
    "facilitator",
    "analyst",
    "sales",
    "client",
    "auditor",
]


class KeycloakClient:
    """Client for Keycloak OIDC authentication."""

    def __init__(
        self,
        server_url: Optional[str] = None,
        realm: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.server_url = (server_url or settings.keycloak_url).rstrip("/")
        self.realm = realm or settings.keycloak_realm
        self.client_id = client_id or settings.keycloak_client_id
        self.client_secret = client_secret or settings.keycloak_client_secret

        self.token_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"
        self.userinfo_url = (
            f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
        )
        self.certs_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/certs"
        self.admin_url = f"{self.server_url}/admin/realms/{self.realm}"

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT access token against Keycloak JWKS."""
        global _jwks_cache

        try:
            # Decode without verification first to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                logger.warning("token_missing_kid")
                return None

            # Fetch JWKS if not cached
            rsa_key = None
            if _jwks_cache:
                for key in _jwks_cache.get("keys", []):
                    if key.get("kid") == kid:
                        rsa_key = key
                        break

            if not rsa_key:
                # Ключ не найден в кэше — обновляем JWKS и ищем снова
                _jwks_cache = await self._fetch_jwks()
                for key in (_jwks_cache or {}).get("keys", []):
                    if key.get("kid") == kid:
                        rsa_key = key
                        break

            if not rsa_key:
                logger.warning("key_not_found_in_jwks", kid=kid)
                return None

            # Verify and decode token
            from jose.utils import base64url_decode
            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
            import json

            # Convert JWK to RSA public key
            n = int.from_bytes(base64url_decode(rsa_key["n"].encode()), byteorder="big")
            e = int.from_bytes(base64url_decode(rsa_key["e"].encode()), byteorder="big")
            public_key = RSAPublicNumbers(e, n).public_key()

            # Подпись и срок действия проверяются; iss/aud зависят от окружения
            # (локальный: localhost:8080, прод: audit.netbrainpower.ru/auth) и не верифицируются
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False, "verify_iss": False},
            )

            return payload

        except JWTError as e:
            logger.warning("token_verification_failed", error=str(e))
            return None
        except Exception as e:
            import traceback
            logger.error("token_verification_error", error=str(e), trace=str(traceback.format_exc()).splitlines()[-6:])
            return None

    async def _fetch_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Keycloak."""
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(self.certs_url, timeout=10.0)
            response.raise_for_status()
            return response.json()

    async def get_user_roles(self, token_payload: Dict[str, Any]) -> List[str]:
        """Extract user roles from token payload."""
        roles = []

        # Realm roles
        realm_access = token_payload.get("realm_access", {})
        roles.extend(realm_access.get("roles", []))

        # Client roles
        resource_access = token_payload.get("resource_access", {})
        client_roles = resource_access.get(self.client_id, {})
        roles.extend(client_roles.get("roles", []))

        # Filter to valid platform roles
        return [r for r in roles if r in VALID_ROLES]

    async def list_users(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Список пользователей realm (операторы платформы)."""
        try:
            admin_token = await self._get_admin_token()
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.admin_url}/users",
                    params={"max": limit, "briefRepresentation": "false"},
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                users = response.json()
            return [
                {
                    "user_id": u.get("id"),
                    "username": u.get("username"),
                    "email": u.get("email"),
                    "first_name": u.get("firstName") or "",
                    "last_name": u.get("lastName") or "",
                    "enabled": bool(u.get("enabled")),
                    "service_account": u.get("serviceAccountClientId") is not None
                    or str(u.get("username", "")).startswith("service-account-"),
                }
                for u in users
            ]
        except Exception as e:
            logger.error("keycloak_list_users_error", error=str(e))
            return []

    async def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя realm."""
        try:
            admin_token = await self._get_admin_token()
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.delete(
                    f"{self.admin_url}/users/{user_id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10.0,
                )
                return response.status_code in (200, 204)
        except Exception as e:
            logger.error("keycloak_delete_user_error", error=str(e))
            return False

    async def get_realm_smtp(self) -> Dict[str, Any]:
        """SMTP-конфигурация realm (пароль маскируется)."""
        try:
            admin_token = await self._get_admin_token()
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.admin_url}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                rep = response.json()
            smtp = rep.get("smtpServer") or {}
            masked = dict(smtp)
            if masked.get("password"):
                masked["password"] = "********"
            return {"configured": bool(smtp), "smtp": masked}
        except Exception as e:
            logger.error("keycloak_get_realm_smtp_error", error=str(e))
            return {"configured": False, "smtp": {}}

    async def set_realm_smtp(self, smtp: Dict[str, Any]) -> bool:
        """Установить SMTP-конфигурацию realm (полный rep: get → modify → put)."""
        try:
            admin_token = await self._get_admin_token()
            async with httpx.AsyncClient(verify=False) as client:
                rep_resp = await client.get(
                    f"{self.admin_url}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10.0,
                )
                rep_resp.raise_for_status()
                rep = rep_resp.json()
                rep["smtpServer"] = smtp
                upd = await client.put(
                    f"{self.admin_url}",
                    json=rep,
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=15.0,
                )
                return upd.status_code in (200, 204)
        except Exception as e:
            logger.error("keycloak_set_realm_smtp_error", error=str(e))
            return False

    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        roles: List[str],
        password: Optional[str] = None,
        required_actions: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create user in Keycloak.

        required_actions (например ['VERIFY_EMAIL','UPDATE_PASSWORD']) — создать
        без пароля и отправить письмо с действиями (нужен SMTP в realm).
        """
        try:
            temp_password = password or __import__("secrets").token_urlsafe(9)
            admin_token = await self._get_admin_token()

            user_data = {
                "username": email,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": False,
                **(
                    {"requiredActions": required_actions}
                    if required_actions
                    else {"credentials": [{"type": "password", "temporary": True, "value": temp_password}]}
                ),
            }

            async with httpx.AsyncClient(verify=False) as client:
                # Create user
                response = await client.post(
                    f"{self.admin_url}/users",
                    json=user_data,
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=10.0,
                )

                if response.status_code not in (201, 409):
                    logger.error(
                        "keycloak_user_creation_failed",
                        status=response.status_code,
                        body=response.text,
                    )
                    return None

                # Get user ID
                user_id = response.headers.get("Location", "").split("/")[-1]

                if not user_id:
                    # User already exists, find by email
                    search = await client.get(
                        f"{self.admin_url}/users",
                        params={"email": email, "exact": True},
                        headers={"Authorization": f"Bearer {admin_token}"},
                    )
                    users = search.json()
                    if users:
                        user_id = users[0]["id"]

                # Assign roles
                for role_name in roles:
                    await self._assign_role(admin_token, user_id, role_name)

                # Письмо с действиями (если запрошено)
                email_sent = False
                if required_actions and user_id:
                    try:
                        act_resp = await client.get(
                            f"{self.admin_url}/users/{user_id}/execute-actions-email",
                            params={"lifespan": 86400},
                            headers={"Authorization": f"Bearer {admin_token}"},
                            timeout=10.0,
                        )
                        email_sent = act_resp.status_code in (200, 204)
                        if not email_sent:
                            logger.warning("keycloak_actions_email_failed",
                                           status=act_resp.status_code)
                    except Exception as mail_err:
                        logger.error("keycloak_actions_email_error", error=str(mail_err))
                    if not email_sent:
                        # fallback: временный пароль вместо письма
                        await client.put(
                            f"{self.admin_url}/users/{user_id}/reset-password",
                            json={"type": "password", "temporary": True, "value": temp_password},
                            headers={"Authorization": f"Bearer {admin_token}"},
                            timeout=10.0,
                        )
                logger.info("keycloak_user_created", user_id=user_id, email=email)
                return {"user_id": user_id, "temp_password": temp_password, "email_sent": email_sent}

        except Exception as e:
            logger.error("keycloak_create_user_error", error=str(e))
            return None

    async def _get_admin_token(self) -> str:
        """Get admin access token."""
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def _assign_role(self, admin_token: str, user_id: str, role_name: str):
        """Assign realm role to user."""
        async with httpx.AsyncClient(verify=False) as client:
            # Get role
            role_resp = await client.get(
                f"{self.admin_url}/roles/{role_name}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            if role_resp.status_code != 200:
                logger.warning("role_not_found", role=role_name)
                return

            role_data = role_resp.json()

            # Assign role
            await client.post(
                f"{self.admin_url}/users/{user_id}/role-mappings/realm",
                json=[role_data],
                headers={"Authorization": f"Bearer {admin_token}"},
            )