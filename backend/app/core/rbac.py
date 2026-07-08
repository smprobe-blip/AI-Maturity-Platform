"""Role-Based Access Control definitions."""

from enum import Enum
from typing import List, Set


class Role(str, Enum):
    """Available roles in the system."""
    
    SUPER_ADMIN = "super_admin"
    FACILITATOR = "facilitator"
    ANALYST = "analyst"
    SALES = "sales"
    CLIENT = "client"
    AUDITOR = "auditor"


# Permission matrix: what each role can do
ROLE_PERMISSIONS: dict[Role, Set[str]] = {
    Role.SUPER_ADMIN: {
        "audit:read", "audit:write", "audit:delete", "audit:export",
        "user:read", "user:write", "user:delete", "user:invite",
        "benchmark:read", "benchmark:recalculate",
        "export:create", "export:download",
        "dashboard:business", "dashboard:scientific", "dashboard:operations", "dashboard:quality",
        "settings:read", "settings:write",
        "audit_log:read",
        "l0_data:access",  # Полный доступ к персональным данным
        "l3_data:access",  # Анонимизированные агрегаты
    },
    Role.FACILITATOR: {
        "audit:read", "audit:write", "audit:export",
        "benchmark:read", "benchmark:recalculate",
        "dashboard:business", "dashboard:operations",
        "l0_data:access",  # Только свои аудиты
        "l3_data:access",
    },
    Role.ANALYST: {
        "audit:read", "audit:export",
        "benchmark:read",
        "export:create", "export:download",
        "dashboard:scientific", "dashboard:quality",
        "l3_data:access",  # Только агрегаты
    },
    Role.SALES: {
        "audit:read",
        "dashboard:business",
        "l0_data:access",  # Только email + компания
    },
    Role.AUDITOR: {
        "audit:read",
        "benchmark:read",
        "dashboard:scientific",
        "l3_data:access",
    },
    Role.CLIENT: {
        "audit:read",  # Только свой аудит
    },
}


def has_permission(role: Role, permission: str) -> bool:
    """Check if role has specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: Role) -> List[str]:
    """Get all permissions for a role."""
    return sorted(ROLE_PERMISSIONS.get(role, set()))


# Resource-level access: what fields can each role see
ROLE_VISIBLE_FIELDS: dict[Role, Set[str]] = {
    Role.SUPER_ADMIN: {
        "company_profile", "contact", "raw_responses",
        "calculated_indices", "qualitative_insights",
        "financial_outcomes", "audit_events",
    },
    Role.FACILITATOR: {
        "company_profile", "contact", "raw_responses",
        "calculated_indices",
    },
    Role.ANALYST: {
        "company_profile", "raw_responses",
        "calculated_indices", "qualitative_insights",
    },
    Role.SALES: {
        "company_profile", "contact",  # Только email + компания
    },
    Role.AUDITOR: {
        "calculated_indices",  # Только агрегаты
    },
    Role.CLIENT: {
        "company_profile", "raw_responses",
        "calculated_indices",
    },
}


def filter_audit_by_role(audit: dict, role: Role) -> dict:
    """Filter audit data based on role permissions."""
    visible = ROLE_VISIBLE_FIELDS.get(role, set())
    return {
        key: value
        for key, value in audit.items()
        if key in visible or key in {"audit_id", "created_at", "updated_at", "status", "audit_type"}
    }