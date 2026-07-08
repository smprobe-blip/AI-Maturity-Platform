"""Audit service — business logic for audits."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from app.core.exceptions import InvalidAuditDataException
from app.models.audit import AuditExpressCreate, CalculatedIndices
from app.services.radar_service import RadarService
from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class AuditService:
    """Service for managing audits."""
    
    def __init__(self):
        self.storage = JSONStorage()
        self.radar_service = RadarService()
    
    def create_express_audit(self, data: AuditExpressCreate) -> Dict[str, Any]:
        """Create express audit (public calculator)."""
        audit_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        # Calculate indices
        calculated_indices = self.radar_service.calculate_indices(data.raw_responses)
        
        # Build audit document
        audit_data = {
            "audit_id": audit_id,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "audit_type": "express",
            "status": "completed",
            "company_profile": data.company_profile.model_dump(),
            "contact": data.contact.model_dump(),
            "raw_responses": [r.model_dump() for r in data.raw_responses],
            "calculated_indices": calculated_indices.model_dump(),
            "audit_events": [
                {
                    "event": "audit_created",
                    "timestamp": created_at.isoformat(),
                    "user": "anonymous",
                }
            ],
        }
        
        # Save to storage
        self.storage.save_audit(audit_data)
        
        logger.info("express_audit_created", audit_id=audit_id)
        
        return audit_data
    
    def get_audit(self, audit_id: str) -> Dict[str, Any]:
        """Get audit by ID."""
        return self.storage.load_audit(audit_id)
    
    def list_audits(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List audits with filters."""
        return self.storage.list_audits(filters=filters, limit=limit, offset=offset)
    
    def archive_audit(self, audit_id: str) -> None:
        """Archive (soft delete) audit."""
        self.storage.delete_audit(audit_id)
        logger.info("audit_archived", audit_id=audit_id)
