"""Audit-related models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RawResponse(BaseModel):
    """Single question response."""
    
    dimension_id: int = Field(..., ge=1, le=7, description="Dimension ID (1-7)")
    question_id: int = Field(..., ge=1, le=5, description="Question ID within dimension (1-5)")
    score: int = Field(..., ge=1, le=5, description="Score (1-5)")
    time_to_answer_sec: Optional[float] = Field(None, ge=0, description="Time to answer in seconds")
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="Confidence level (1-5)")


class CompanyProfile(BaseModel):
    """Anonymized company profile."""
    
    industry: str = Field(..., description="Industry sector")
    company_size: str = Field(..., description="Company size category")
    region: str = Field(..., description="Geographic region")
    ai_experience_years: Optional[int] = Field(None, ge=0, description="Years of AI experience")
    annual_it_budget_millions: Optional[float] = Field(None, ge=0, description="Annual IT budget in millions")


class ContactInfo(BaseModel):
    """Contact information."""
    
    email: EmailStr = Field(..., description="Contact email")
    name: Optional[str] = Field(None, description="Contact name")
    position: Optional[str] = Field(None, description="Contact position")
    phone: Optional[str] = Field(None, description="Contact phone")
    consent_to_process_data: bool = Field(..., description="Consent to process personal data")


class CalculatedIndices(BaseModel):
    """Calculated maturity indices."""
    
    dimension_scores: Dict[str, float] = Field(
        ..., description="Scores by dimension (dimension_id: score)"
    )
    composite_score: float = Field(..., ge=0, le=5, description="Composite maturity score")
    maturity_level: str = Field(..., description="Maturity level (L1-L5)")
    roi_estimate_percent: Optional[float] = Field(None, description="Estimated ROI %")
    tco_estimate_millions: Optional[float] = Field(None, description="Estimated TCO in millions")


class AuditExpressCreate(BaseModel):
    """Express audit creation request (public calculator)."""
    
    company_profile: CompanyProfile
    contact: ContactInfo
    raw_responses: List[RawResponse] = Field(..., min_length=35, max_length=35)
    
    @field_validator("raw_responses")
    @classmethod
    def validate_responses(cls, v: List[RawResponse]) -> List[RawResponse]:
        """Validate that all 35 questions are answered."""
        if len(v) != 35:
            raise ValueError("Exactly 35 responses required (7 dimensions × 5 questions)")
        
        # Check that each dimension has exactly 5 responses
        dimension_counts = {}
        for response in v:
            dim_id = response.dimension_id
            dimension_counts[dim_id] = dimension_counts.get(dim_id, 0) + 1
        
        for dim_id in range(1, 8):
            if dimension_counts.get(dim_id, 0) != 5:
                raise ValueError(f"Dimension {dim_id} must have exactly 5 responses")
        
        return v


class AuditExpressResponse(BaseModel):
    """Express audit response."""
    
    audit_id: str = Field(..., description="Unique audit ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    calculated_indices: CalculatedIndices
    report_url: Optional[str] = Field(None, description="URL to PDF report")
    message: str = Field(..., description="Success message")


class AuditCreate(BaseModel):
    """Full audit creation request (admin)."""
    
    company_profile: CompanyProfile
    contact: ContactInfo
    raw_responses: List[RawResponse]
    qualitative_insights: Optional[Dict[str, Any]] = Field(
        None, description="Qualitative insights (quotes, themes)"
    )
    financial_outcomes: Optional[Dict[str, Any]] = Field(
        None, description="Financial outcomes (TCO, ROI, NBP)"
    )


class AuditResponse(BaseModel):
    """Full audit response."""
    
    audit_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    company_profile: CompanyProfile
    contact: ContactInfo
    raw_responses: List[RawResponse]
    calculated_indices: CalculatedIndices
    qualitative_insights: Optional[Dict[str, Any]] = None
    financial_outcomes: Optional[Dict[str, Any]] = None
    audit_events: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = Field(..., description="Audit status")