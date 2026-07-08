"""Admin audit service — extends AuditService with admin operations."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from app.core.exceptions import AuditNotFoundException, InvalidAuditDataException
from app.models.admin import AuditFilters
from app.models.audit import AuditCreate, CalculatedIndices
from app.services.radar_service import RadarService
from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class AdminAuditService:
    """Admin operations on audits."""
    
    def __init__(self):
        self.storage = JSONStorage()
        self.radar_service = RadarService()
    
    def list_audits(self, filters: AuditFilters, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List audits with advanced filters."""
        # Get all audits
        all_audits = self.storage.list_audits(limit=10000, offset=0)
        
        # Apply filters
        filtered = []
        for audit in all_audits:
            if not self._matches_filters(audit, filters):
                continue
            filtered.append(audit)
        
        # Sort by created_at (newest first)
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        total = len(filtered)
        paginated = filtered[offset : offset + limit]
        
        return {
            "items": paginated,
            "total": total,
            "page": offset // limit + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
        }
    
    def _matches_filters(self, audit: Dict[str, Any], filters: AuditFilters) -> bool:
        """Check if audit matches all filters."""
        profile = audit.get("company_profile", {})
        indices = audit.get("calculated_indices", {})
        created_at = audit.get("created_at", "")
        
        if filters.industry and profile.get("industry") != filters.industry:
            return False
        
        if filters.company_size and profile.get("company_size") != filters.company_size:
            return False
        
        if filters.region and profile.get("region") != filters.region:
            return False
        
        if filters.status and audit.get("status") != filters.status:
            return False
        
        if filters.maturity_level:
            level = indices.get("maturity_level", "")
            if not level.startswith(filters.maturity_level):
                return False
        
        if filters.date_from and created_at < filters.date_from.isoformat():
            return False
        
        if filters.date_to and created_at > filters.date_to.isoformat():
            return False
        
        if filters.min_score is not None:
            if indices.get("composite_score", 0) < filters.min_score:
                return False
        
        if filters.max_score is not None:
            if indices.get("composite_score", 0) > filters.max_score:
                return False
        
        if filters.search:
            search_lower = filters.search.lower()
            searchable = (
                f"{profile.get('industry', '')} "
                f"{profile.get('company_size', '')} "
                f"{profile.get('region', '')} "
                f"{audit.get('audit_id', '')}"
            ).lower()
            if search_lower not in searchable:
                return False
        
        return True
    
    def create_audit(
        self, data: AuditCreate, created_by: str, nda_signed: bool = False
    ) -> Dict[str, Any]:
        """Create a full audit (admin only)."""
        audit_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        # Calculate indices
        from app.models.audit import RawResponse
        raw_responses = [RawResponse(**r) if isinstance(r, dict) else r for r in data.raw_responses]
        calculated_indices = self.radar_service.calculate_indices(raw_responses)
        
        audit_data = {
            "audit_id": audit_id,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "audit_type": "full",
            "status": "completed",
            "created_by": created_by,
            "nda_signed": nda_signed,
            "company_profile": data.company_profile.model_dump(),
            "contact": data.contact.model_dump(),
            "raw_responses": [r.model_dump() for r in raw_responses],
            "calculated_indices": calculated_indices.model_dump(),
            "qualitative_insights": data.qualitative_insights,
            "financial_outcomes": data.financial_outcomes,
            "audit_events": [
                {
                    "event": "audit_created",
                    "timestamp": created_at.isoformat(),
                    "user": created_by,
                    "details": {"nda_signed": nda_signed},
                }
            ],
        }
        
        self.storage.save_audit(audit_data)
        logger.info("admin_audit_created", audit_id=audit_id, created_by=created_by)
        
        return audit_data
    
    def update_audit(
        self, audit_id: str, updates: Dict[str, Any], updated_by: str
    ) -> Dict[str, Any]:
        """Update audit fields."""
        audit = self.storage.load_audit(audit_id)
        
        # Recalculate indices if raw_responses changed
        if "raw_responses" in updates:
            from app.models.audit import RawResponse
            raw_responses = [RawResponse(**r) if isinstance(r, dict) else r for r in updates["raw_responses"]]
            new_indices = self.radar_service.calculate_indices(raw_responses)
            updates["calculated_indices"] = new_indices.model_dump()
        
        # Apply updates
        for key, value in updates.items():
            if key not in ["audit_id", "created_at"]:
                audit[key] = value
        
        audit["updated_at"] = datetime.now().isoformat()
        audit["audit_events"].append({
            "event": "audit_updated",
            "timestamp": audit["updated_at"],
            "user": updated_by,
            "details": {"updated_fields": list(updates.keys())},
        })
        
        self.storage.save_audit(audit)
        logger.info("admin_audit_updated", audit_id=audit_id, updated_by=updated_by)
        
        return audit
    
    def delete_audit(self, audit_id: str, deleted_by: str) -> None:
        """Archive (soft delete) an audit."""
        self.storage.delete_audit(audit_id)
        logger.info("admin_audit_deleted", audit_id=audit_id, deleted_by=deleted_by)