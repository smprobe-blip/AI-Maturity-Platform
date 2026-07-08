"""Tests for audit models."""

import pytest
from pydantic import ValidationError

from app.models.audit import (
    AuditExpressCreate,
    CalculatedIndices,
    CompanyProfile,
    ContactInfo,
    RawResponse,
)


class TestRawResponse:
    """Tests for RawResponse model."""
    
    def test_valid_raw_response(self):
        """Test valid raw response."""
        response = RawResponse(
            dimension_id=1,
            question_id=1,
            score=3,
            time_to_answer_sec=15.5,
            confidence_level=4,
        )
        assert response.dimension_id == 1
        assert response.question_id == 1
        assert response.score == 3
        assert response.time_to_answer_sec == 15.5
        assert response.confidence_level == 4
    
    def test_invalid_dimension_id_too_low(self):
        """Test dimension_id < 1 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RawResponse(dimension_id=0, question_id=1, score=3)
        assert "dimension_id" in str(exc_info.value)
    
    def test_invalid_dimension_id_too_high(self):
        """Test dimension_id > 7 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RawResponse(dimension_id=8, question_id=1, score=3)
        assert "dimension_id" in str(exc_info.value)
    
    def test_invalid_score_too_low(self):
        """Test score < 1 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RawResponse(dimension_id=1, question_id=1, score=0)
        assert "score" in str(exc_info.value)
    
    def test_invalid_score_too_high(self):
        """Test score > 5 raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RawResponse(dimension_id=1, question_id=1, score=6)
        assert "score" in str(exc_info.value)
    
    def test_optional_fields(self):
        """Test optional fields can be None."""
        response = RawResponse(dimension_id=1, question_id=1, score=3)
        assert response.time_to_answer_sec is None
        assert response.confidence_level is None


class TestCompanyProfile:
    """Tests for CompanyProfile model."""
    
    def test_valid_company_profile(self):
        """Test valid company profile."""
        profile = CompanyProfile(
            industry="Retail",
            company_size="Large (1000+)",
            region="Russia",
            ai_experience_years=2,
            annual_it_budget_millions=50.0,
        )
        assert profile.industry == "Retail"
        assert profile.company_size == "Large (1000+)"
        assert profile.ai_experience_years == 2
    
    def test_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            CompanyProfile(
                company_size="Large",
                region="Russia",
            )
    
    def test_negative_ai_experience(self):
        """Test negative ai_experience_years raises error."""
        with pytest.raises(ValidationError):
            CompanyProfile(
                industry="Retail",
                company_size="Large",
                region="Russia",
                ai_experience_years=-1,
            )


class TestContactInfo:
    """Tests for ContactInfo model."""
    
    def test_valid_contact(self):
        """Test valid contact info."""
        contact = ContactInfo(
            email="test@example.com",
            name="John Doe",
            consent_to_process_data=True,
        )
        assert contact.email == "test@example.com"
        assert contact.consent_to_process_data is True
    
    def test_invalid_email(self):
        """Test invalid email raises error."""
        with pytest.raises(ValidationError):
            ContactInfo(
                email="not-an-email",
                consent_to_process_data=True,
            )
    
    def test_consent_required(self):
        """Test consent_to_process_data is required."""
        with pytest.raises(ValidationError):
            ContactInfo(email="test@example.com")


class TestAuditExpressCreate:
    """Tests for AuditExpressCreate model."""
    
    def test_valid_express_audit(
        self,
        sample_raw_responses: list,
        sample_company_profile: dict,
        sample_contact: dict,
    ):
        """Test valid express audit creation."""
        audit = AuditExpressCreate(
            company_profile=sample_company_profile,
            contact=sample_contact,
            raw_responses=sample_raw_responses,
        )
        assert len(audit.raw_responses) == 35
    
    def test_too_few_responses(
        self,
        sample_company_profile: dict,
        sample_contact: dict,
    ):
        """Test < 35 responses raises error."""
        with pytest.raises(ValidationError) as exc_info:
            AuditExpressCreate(
                company_profile=sample_company_profile,
                contact=sample_contact,
                raw_responses=[],
            )
        assert "35 responses" in str(exc_info.value) or "min_length" in str(exc_info.value)
    
    def test_incomplete_dimensions(
        self,
        sample_company_profile: dict,
        sample_contact: dict,
    ):
        """Test incomplete dimensions raises error."""
        # Only 30 responses (missing dimension 7)
        responses = []
        for dim_id in range(1, 7):
            for q_id in range(1, 6):
                responses.append({
                    "dimension_id": dim_id,
                    "question_id": q_id,
                    "score": 3,
                })
        
        with pytest.raises(ValidationError) as exc_info:
            AuditExpressCreate(
                company_profile=sample_company_profile,
                contact=sample_contact,
                raw_responses=responses,
            )
        assert "Dimension" in str(exc_info.value) or "exactly 5" in str(exc_info.value)


class TestCalculatedIndices:
    """Tests for CalculatedIndices model."""
    
    def test_valid_indices(self):
        """Test valid calculated indices."""
        indices = CalculatedIndices(
            dimension_scores={"1": 3.5, "2": 4.0, "3": 2.8},
            composite_score=3.43,
            maturity_level="L3 — Defined",
            roi_estimate_percent=243.0,
            tco_estimate_millions=51.45,
        )
        assert indices.composite_score == 3.43
        assert indices.maturity_level == "L3 — Defined"
    
    def test_composite_score_out_of_range(self):
        """Test composite_score out of range raises error."""
        with pytest.raises(ValidationError):
            CalculatedIndices(
                dimension_scores={},
                composite_score=6.0,  # > 5.0
                maturity_level="L5",
            )