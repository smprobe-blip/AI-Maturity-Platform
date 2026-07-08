"""Tests for AuditService."""

import pytest

from app.models.audit import AuditExpressCreate, CompanyProfile, ContactInfo, RawResponse
from app.services.audit_service import AuditService


class TestAuditService:
    """Tests for AuditService."""
    
    @pytest.fixture
    def audit_service(self, json_storage) -> AuditService:
        """AuditService instance with test storage."""
        service = AuditService()
        service.storage = json_storage  # Override with test storage
        return service
    
    def test_create_express_audit(
        self,
        audit_service: AuditService,
        sample_audit_express_data: dict,
    ):
        """Test express audit creation."""
        data = AuditExpressCreate(**sample_audit_express_data)
        audit = audit_service.create_express_audit(data)
        
        assert "audit_id" in audit
        assert audit["status"] == "completed"
        assert audit["audit_type"] == "express"
        assert "calculated_indices" in audit
        assert len(audit["raw_responses"]) == 35
    
    def test_get_audit(
        self,
        audit_service: AuditService,
        sample_audit_express_data: dict,
    ):
        """Test getting audit by ID."""
        # Create audit
        data = AuditExpressCreate(**sample_audit_express_data)
        created = audit_service.create_express_audit(data)
        audit_id = created["audit_id"]
        
        # Retrieve audit
        retrieved = audit_service.get_audit(audit_id)
        
        assert retrieved["audit_id"] == audit_id
        assert retrieved["status"] == "completed"
    
    def test_list_audits(
        self,
        audit_service: AuditService,
        sample_audit_express_data: dict,
    ):
        """Test listing audits."""
        # Create 3 audits
        for i in range(3):
            data = AuditExpressCreate(**sample_audit_express_data)
            audit_service.create_express_audit(data)
        
        # List audits
        audits = audit_service.list_audits(limit=10, offset=0)
        
        assert len(audits) == 3
    
    def test_archive_audit(
        self,
        audit_service: AuditService,
        sample_audit_express_data: dict,
    ):
        """Test archiving audit."""
        # Create audit
        data = AuditExpressCreate(**sample_audit_express_data)
        created = audit_service.create_express_audit(data)
        audit_id = created["audit_id"]
        
        # Archive
        audit_service.archive_audit(audit_id)
        
        # Check status
        retrieved = audit_service.get_audit(audit_id)
        assert retrieved["status"] == "archived"