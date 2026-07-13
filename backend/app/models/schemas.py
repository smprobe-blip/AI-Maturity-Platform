"""Pydantic schemas for API requests and responses.
Priority 1: 35 questions, patterns, top-3, gap analysis, upsell.
"""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Pattern diagnosis models
# ============================================================

class PatternInfo(BaseModel):
    """Dynamic pattern diagnosis from radar chart."""
    pattern_type: Literal[
        'compressed_circle',
        'right_skew',
        'left_skew',
        'star_with_gaps',
        'benchmark_parity',
        'balanced'
    ]
    diagnosis: str
    recommendation: str
    severity: Literal['critical', 'warning', 'info', 'success'] = 'info'


# ============================================================
# Top-3 analysis models
# ============================================================

class BottleneckItem(BaseModel):
    """Weak dimension (bottleneck)."""
    dimension_id: str
    dimension_name: str
    score: float
    severity: Literal['critical', 'warning', 'info']
    weight: float


class AnchorItem(BaseModel):
    """Strong dimension (anchor for change)."""
    dimension_id: str
    dimension_name: str
    score: float
    strength: Literal['strong', 'moderate', 'weak']
    weight: float


# ============================================================
# Upsell trigger models
# ============================================================

class UpsellTrigger(BaseModel):
    """Monetization trigger based on weak dimensions."""
    type: Literal['fear_of_loss', 'bottleneck', 'new_roles', 'methodology']
    dimension_id: str
    dimension_name: str
    score: float
    risk: str
    service: str
    price_hint: str


# ============================================================
# Gap analysis models
# ============================================================

class DimensionGap(BaseModel):
    """Gap for single dimension."""
    current: float
    target: float
    gap: float
    priority: Literal['high', 'medium', 'low']


class GapAnalysis(BaseModel):
    """Gap analysis between current and target state."""
    dimension_gaps: Dict[str, DimensionGap]
    weighted_total_gap: float
    priority_axes: List[str]


# ============================================================
# Calculated indices (main result)
# ============================================================

class CalculatedIndices(BaseModel):
    """Full set of calculated maturity indices."""
    composite_score: float
    maturity_level: str
    dimension_scores: Dict[str, float]
    roi_estimate_percent: Optional[float] = None
    tco_estimate_millions: Optional[float] = None
    top3_bottlenecks: List[BottleneckItem] = []
    top3_anchors: List[AnchorItem] = []
    pattern: Optional[PatternInfo] = None
    gap_analysis: Optional[GapAnalysis] = None
    benchmark_scores: Optional[Dict[str, float]] = None  # Industry benchmark


# ============================================================
# Audit request/response models
# ============================================================

class ExpressAuditRequest(BaseModel):
    """Request body for express audit creation (35 questions)."""
    company_industry: str = Field(..., description="Industry code (retail, finance, it, etc.)")
    company_size: Literal['small', 'medium', 'large', 'enterprise']
    contact_email: EmailStr
    contact_name: Optional[str] = None
    report_type: Literal['express', 'executive', 'comprehensive'] = 'express'
    responses: Dict[str, Any] = Field(
        ...,
        description="Nested format: {'1': {'1': 4, '2': 3, ...}, ...} or flat: {'1': 3.5, ...}"
    )
    target_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="Target scores for gap analysis: {'1': 4.5, '2': 4.0, ...}"
    )
    pdn_consent: bool = Field(..., description="152-FZ personal data consent")


class AuditResponse(BaseModel):
    """Public audit response with calculated indices."""
    audit_id: str
    created_at: str
    report_type: str
    company_profile: Dict[str, Any]
    calculated_indices: CalculatedIndices
    recommendations: List[str] = []
    upsell_triggers: List[UpsellTrigger] = []


class EmailReportRequest(BaseModel):
    """Request to send audit report via email."""
    email: EmailStr


class BenchmarkResponse(BaseModel):
    """Industry benchmark data."""
    industry: str
    sample_size: int
    dimension_means: Dict[str, float]
    composite_mean: float
    composite_median: float
    percentiles: Dict[str, float]