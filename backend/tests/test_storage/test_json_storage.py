"""Tests for JSON storage."""

import pytest

from app.storage.json_storage import JSONStorage
from app.core.exceptions import AuditNotFoundException


class TestJSONStorage:
    """Tests for JSONStorage."""
    
    def test_save_and_load_audit(self, json_storage: JSONStorage):
        """Test saving and loading audit."""
        audit_data = {
            "audit_id": "test-audit-123",
            "status": "completed",
            "data": {"test": "value"},
        }
        
        # Save
        path = json_storage.save_audit(audit_data)
        assert path.endswith("audit_test-audit-123.json")
        
        # Load
        loaded = json_storage.load_audit("test-audit-123")
        assert loaded["audit_id"] == "test-audit-123"
        assert loaded["status"] == "completed"
    
    def test_load_nonexistent_audit(self, json_storage: JSONStorage):
        """Test loading non-existent audit raises error."""
        with pytest.raises(AuditNotFoundException):
            json_storage.load_audit("non-existent-id")
    
    def test_list_audits(self, json_storage: JSONStorage):
        """Test listing audits."""
        # Create 3 audits
        for i in range(3):
            json_storage.save_audit({
                "audit_id": f"audit-{i}",
                "status": "completed",
                "created_at": "2026-01-01T00:00:00",
            })
        
        # List
        audits = json_storage.list_audits(limit=10, offset=0)
        assert len(audits) == 3
    
    def test_delete_audit(self, json_storage: JSONStorage):
        """Test deleting (archiving) audit."""
        audit_data = {
            "audit_id": "test-delete",
            "status": "completed",
        }
        json_storage.save_audit(audit_data)
        
        # Delete
        json_storage.delete_audit("test-delete")
        
        # Check status
        loaded = json_storage.load_audit("test-delete")
        assert loaded["status"] == "archived"