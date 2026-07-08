"""Pydantic models for Admin API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.rbac import Role


# ============ AUDIT FILTERS ============

class AuditFilters(BaseModel):
    """Filters for listing audits."""
    
    industry: Optional[str] = None
    company_size: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(completed|in_progress|archived)$")
    maturity_level: Optional[str] = Field(None, pattern="^L[1-5]")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_score: Optional[float] = Field(None, ge=0, le=5)
    max_score: Optional[float] = Field(None, ge=0, le=5)
    search: Optional[str] = Field(None, min_length=2)


# ============ USER MANAGEMENT ============

class UserInvite(BaseModel):
    """Invite a new user."""
    
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    role: Role
    send_invitation_email: bool = True


class UserUpdate(BaseModel):
    """Update user information."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User information response."""
    
    user_id: str
    email: EmailStr
    name: Optional[str]
    role: Role
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


# ============ EXPORTS ============

class ExportFormat(str):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request for data export."""
    
    format: str = Field(..., pattern="^(json|csv|parquet|pdf)$")
    filters: AuditFilters = Field(default_factory=AuditFilters)
    include_fields: List[str] = Field(
        default_factory=lambda: ["company_profile", "calculated_indices"],
        description="Fields to include in export",
    )
    anonymization_level: str = Field(
        "L3",
        pattern="^(L0|L1|L2|L3)$",
        description="Data anonymization level",
    )
    include_benchmarks: bool = False
    include_raw_responses: bool = False
    
    @field_validator("anonymization_level")
    @classmethod
    def validate_anonymization(cls, v: str) -> str:
        """Validate anonymization level."""
        return v


class ExportResponse(BaseModel):
    """Export creation response."""
    
    export_id: str
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")
    download_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime
    expires_at: datetime


class ExportHistoryItem(BaseModel):
    """Single export history entry."""
    
    export_id: str
    format: str
    status: str
    file_size_bytes: Optional[int] = None
    created_at: datetime
    created_by: str
    filters_applied: Dict[str, Any]


# ============ DASHBOARD ============

class BusinessDashboardResponse(BaseModel):
    """Business metrics dashboard."""
    
    total_audits: int
    audits_this_month: int
    audits_this_week: int
    conversion_rate: float  # express → full audit conversion
    average_maturity_score: float
    top_industries: List[Dict[str, Any]]
    growth_trend: List[Dict[str, Any]]  # monthly counts


class ScientificDashboardResponse(BaseModel):
    """Scientific/research metrics dashboard."""
    
    sample_size: int
    cronbach_alpha_by_dimension: Dict[str, float]
    factor_analysis_summary: Dict[str, Any]
    distribution_by_maturity_level: Dict[str, int]
    correlation_matrix: Dict[str, Dict[str, float]]


class OperationsDashboardResponse(BaseModel):
    """Operational metrics dashboard."""
    
    average_completion_time_sec: float
    completion_rate: float  # started / completed
    average_time_per_question_sec: float
    top_dropout_questions: List[Dict[str, Any]]
    system_performance: Dict[str, float]


class QualityDashboardResponse(BaseModel):
    """Data quality metrics dashboard."""
    
    completeness_score: float  # 0-100
    consistency_score: float  # 0-100
    outlier_count: int
    duplicate_count: int
    data_freshness_days: int
    validation_issues: List[Dict[str, Any]]


# ============ BENCHMARKS ============

class BenchmarkResponse(BaseModel):
    """Industry benchmark data."""
    
    industry: str
    sample_size: int
    average_score: float
    median_score: float
    std_dev: float
    percentiles: Dict[str, float]  # p25, p50, p75, p90
    by_dimension: Dict[str, Dict[str, float]]  # dimension → stats
    last_updated: datetime


class BenchmarkRecalculateRequest(BaseModel):
    """Request to recalculate benchmarks."""
    
    industries: Optional[List[str]] = None
    force_full_recalculation: bool = False


# ============ SETTINGS ============

class MethodologySettings(BaseModel):
    """Methodology settings (weights, etc.)."""
    
    dimension_weights: Dict[str, float]
    maturity_thresholds: Dict[str, float]
    roi_formula_params: Dict[str, float]
    tco_formula_params: Dict[str, float]
    version: str
    updated_at: datetime
    updated_by: str


class IntegrationSettings(BaseModel):
    """Integration settings."""
    
    baserow_enabled: bool
    baserow_table_id: Optional[int]
    smtp_enabled: bool
    smtp_host: Optional[str]
    yookassa_enabled: bool
    yookassa_shop_id: Optional[str]
    keycloak_enabled: bool
    keycloak_realm: Optional[str]


class IntegrationSettingsUpdate(BaseModel):
    """Update integration settings."""
    
    baserow_enabled: Optional[bool] = None
    baserow_api_token: Optional[str] = None
    smtp_enabled: Optional[bool] = None
    smtp_password: Optional[str] = None
    yookassa_enabled: Optional[bool] = None
    yookassa_secret_key: Optional[str] = None


# ============ AUDIT LOG ============

class AuditLogEntry(BaseModel):
    """Admin action audit log entry."""
    
    event_id: str
    timestamp: datetime
    user_id: str
    user_email: str
    action: str  # e.g., "audit.deleted", "user.invited"
    resource_type: str  # e.g., "audit", "user"
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None