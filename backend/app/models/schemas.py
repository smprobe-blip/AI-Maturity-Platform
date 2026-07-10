"""Pydantic schemas for API requests and responses.
v1.1 — Priority 1: 35 questions, patterns, top-3, gap analysis, upsell.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================
# Pattern diagnosis (from pattern_service.py)
# ============================================================

class PatternInfo(BaseModel):
    """Dynamic pattern diagnosis for radar chart."""
    pattern_type: Literal[
        'compressed_circle', 'right_skew', 'left_skew',
        'star_with_gaps', 'benchmark_parity', 'balanced'
    ]
    diagnosis: str
    recommendation: str
    severity: Literal['critical', 'warning', 'info', 'success'] = 'info'


# ============================================================
# Top-3 analysis items
# ============================================================

class BottleneckItem(BaseModel):
    """Top-3 weakest dimension (bottleneck)."""
    dimension_id: str
    dimension_name: str
    score: float
    severity: Literal['critical', 'warning', 'info']
    weight: float = 0.15


class AnchorItem(BaseModel):
    """Top-3 strongest dimension (anchor for change)."""
    dimension_id: str
    dimension_name: str
    score: float
    strength: Literal['strong', 'moderate', 'weak']
    weight: float = 0.15


# ============================================================
# Upsell triggers (monetization)
# ============================================================

class UpsellTrigger(BaseModel):
    """Upsell trigger based on dimension weakness."""
    type: Literal['fear_of_loss', 'bottleneck', 'new_roles', 'methodology']
    dimension_id: str
    dimension_name: str
    score: float
    risk: str
    service: str
    price_hint: str


# ============================================================
# Gap analysis
# ============================================================

class DimensionGap(BaseModel):
    """Gap for single dimension (current vs target)."""
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
# Request schemas
# ============================================================

class ExpressAuditRequest(BaseModel):
    """Request body for express audit creation.

    Supports two response formats (backward compatible):
    1. Flat: {'1': 3.5, '2': 2.0, ...} — legacy 7 sliders
    2. Nested: {'1': {'1': 4, '2': 3, ...}, ...} — 35 questions (Priority 1)
    """
    company_industry: str = Field(..., description="Industry code (retail, finance, it, etc.)")
    company_size: Literal['small', 'medium', 'large', 'enterprise'] = Field(
        ..., description="Company size category"
    )
    contact_email: EmailStr
    contact_name: Optional[str] = None

    report_type: Literal['express', 'executive', 'comprehensive'] = Field(
        default='express',
        description="Report variant: express (free), executive (50k), comprehensive (150k)"
    )

    responses: Dict[str, Union[float, Dict[str, float]]] = Field(
        ...,
        description=(
            "Dimension responses. "
            "Flat format: {'1': 3.5} — single score per axis. "
            "Nested format: {'1': {'1': 4, '2': 3, '3': 5, '4': 2, '5': 4}} — 5 questions per axis."
        ),
    )

    target_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="Target dimension scores for gap analysis (dim_id -> target 1-5)"
    )

    pdn_consent: bool = Field(
        default=False,
        description="Personal data processing consent (required by 152-FZ)"
    )

    @field_validator('pdn_consent')
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                'Personal data processing consent is required (152-ФЗ). '
                'Please check the consent checkbox.'
            )
        return v

    @field_validator('responses')
    @classmethod
    def validate_responses(cls, v: Dict) -> Dict:
        if not v:
            raise ValueError('Responses cannot be empty')
        # Validate that we have at least some dimension IDs
        valid_dims = {'1', '2', '3', '4', '5', '6', '7'}
        provided = set(v.keys())
        if not provided.issubset(valid_dims):
            invalid = provided - valid_dims
            raise ValueError(f'Invalid dimension IDs: {invalid}. Must be 1-7.')
        return v

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    "company_industry": "retail",
                    "company_size": "large",
                    "contact_email": "ceo@example.com",
                    "contact_name": "Ivan Petrov",
                    "report_type": "executive",
                    "responses": {
                        "1": {"1": 4, "2": 3, "3": 5, "4": 2, "5": 4},
                        "2": {"1": 3, "2": 4, "3": 2, "4": 3, "5": 3},
                        "3": {"1": 4, "2": 5, "3": 3, "4": 4, "5": 2},
                        "4": {"1": 3, "2": 2, "3": 4, "4": 3, "5": 4},
                        "5": {"1": 4, "2": 3, "3": 4, "4": 5, "5": 3},
                        "6": {"1": 3, "2": 4, "3": 3, "4": 4, "5": 3},
                        "7": {"1": 2, "2": 3, "3": 2, "4": 3, "5": 2},
                    },
                    "target_scores": {
                        "1": 4.5, "2": 4.0, "3": 4.5, "4": 4.0,
                        "5": 4.5, "6": 4.0, "7": 3.5,
                    },
                    "pdn_consent": True,
                }
            ]
        }
    }


class EmailReportRequest(BaseModel):
    """Request to email audit report."""
    email: EmailStr


# ============================================================
# Response schemas
# ============================================================

class CalculatedIndices(BaseModel):
    """Calculated maturity indices with Priority 1 extensions."""
    composite_score: float
    maturity_level: str
    dimension_scores: Dict[str, float]

    # Financial estimates
    roi_estimate_percent: Optional[float] = None
    tco_estimate_millions: Optional[float] = None

    # Priority 1: Top-3 analysis
    top3_bottlenecks: List[BottleneckItem] = Field(default_factory=list)
    top3_anchors: List[AnchorItem] = Field(default_factory=list)

    # Priority 1: Pattern diagnosis
    pattern: Optional[PatternInfo] = None

    # Priority 1: Gap analysis (current vs target)
    gap_analysis: Optional[GapAnalysis] = None


class AuditResponse(BaseModel):
    """Public audit response (returned to frontend)."""
    audit_id: str
    created_at: str
    report_type: str = 'express'
    company_profile: Dict[str, Any]
    calculated_indices: CalculatedIndices
    recommendations: List[str] = []
    upsell_triggers: List[UpsellTrigger] = []


class BenchmarkResponse(BaseModel):
    """Industry benchmark data."""
    industry: str
    sample_size: int
    dimension_means: Dict[str, float]
    composite_mean: float
    composite_median: float
    percentiles: Dict[str, float]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response (unified format)."""
    error: Dict[str, Any]