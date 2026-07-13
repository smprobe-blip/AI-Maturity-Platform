"""Audit service — main business logic.
Priority 1 + 2.1: integrates radar_service, pattern_service, storage.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from app.models.schemas import (
    AuditResponse,
    CalculatedIndices,
    ExpressAuditRequest,
)
from app.services.radar_service import (
    calculate_indices,
    generate_recommendations,
)


class AuditService:
    """Service for creating and loading audits."""

    def __init__(self):
        """Initialize storage paths."""
        # Try to get path from settings, fallback to default
        try:
            from app.core.config import settings
            raw_path = Path(str(settings.raw_audits_path))
        except (ImportError, AttributeError):
            raw_path = Path(__file__).parent.parent.parent / 'data_storage' / 'raw_audits'
        
        self.raw_path = raw_path
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def create_express_audit(self, req: ExpressAuditRequest) -> AuditResponse:
        """Create new express audit and persist to storage.
        
        Steps:
        1. Generate audit_id (UUID4)
        2. Calculate indices via radar_service
        3. Generate recommendations
        4. Persist to JSON file
        5. Return AuditResponse
        """
        audit_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # 1. Calculate indices (with benchmark auto-loading)
        indices, upsell_triggers = calculate_indices(
            responses=req.responses,
            company_size=req.company_size,
            company_industry=req.company_industry,
            target_scores=req.target_scores,
        )

        # 2. Generate recommendations
        recommendations = generate_recommendations(
            indices.dimension_scores,
            indices.top3_bottlenecks,
            indices.top3_anchors,
        )

        # 3. Build company profile
        company_profile = {
            'industry': req.company_industry,
            'size': req.company_size,
            'anonymized': True,
        }
        if req.contact_name:
            company_profile['contact_name_hash'] = hash(req.contact_name) % (10**8)

        # 4. Build response
        response = AuditResponse(
            audit_id=audit_id,
            created_at=created_at,
            report_type=req.report_type,
            company_profile=company_profile,
            calculated_indices=indices,
            recommendations=recommendations,
            upsell_triggers=upsell_triggers,
        )

        # 5. Persist to JSON
        self._persist_audit(audit_id, response, req)

        return response

    def get_audit(self, audit_id: str) -> Optional[AuditResponse]:
        """Load existing audit by ID.
        
        Searches in year-based folder structure: raw_audits/YYYY/audit_{id}.json
        """
        # Try current year first, then last 3 years
        current_year = datetime.now(timezone.utc).year
        
        for year_offset in range(3):
            year = current_year - year_offset
            file_path = self.raw_path / str(year) / f'audit_{audit_id}.json'
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return AuditResponse(**data)
                except Exception as e:
                    print(f'[audit_service] Error loading {audit_id}: {e}')
                    continue
        
        # Fallback: search in root raw_path (for old audits)
        file_path = self.raw_path / f'audit_{audit_id}.json'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AuditResponse(**data)
            except Exception as e:
                print(f'[audit_service] Error loading {audit_id}: {e}')
        
        return None

    def _persist_audit(
        self,
        audit_id: str,
        response: AuditResponse,
        request: ExpressAuditRequest,
    ) -> None:
        """Persist audit to JSON file with year-based structure.
        
        Structure: raw_audits/YYYY/audit_{id}.json
        Contains both request (responses) and response (calculated indices).
        """
        try:
            # Year-based folder
            year = datetime.now(timezone.utc).year
            year_dir = self.raw_path / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = year_dir / f'audit_{audit_id}.json'
            
            # Combine request + response for full audit record
            audit_record = {
                # Response fields
                'audit_id': response.audit_id,
                'created_at': response.created_at,
                'report_type': response.report_type,
                'company_profile': response.company_profile,
                'calculated_indices': response.calculated_indices.model_dump(),
                'recommendations': response.recommendations,
                'upsell_triggers': [t.model_dump() for t in response.upsell_triggers],
                # Request fields (for analytics)
                'request': {
                    'company_industry': request.company_industry,
                    'company_size': request.company_size,
                    'contact_email': request.contact_email,
                    'contact_name': request.contact_name,
                    'report_type': request.report_type,
                    'responses': request.responses,
                    'target_scores': request.target_scores,
                    'pdn_consent': request.pdn_consent,
                },
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(audit_record, f, ensure_ascii=False, indent=2, default=str)
            
            print(f'[audit_service] Saved audit {audit_id} to {file_path}')
            
        except Exception as e:
            print(f'[audit_service] Error persisting {audit_id}: {e}')
            # Don't fail the request if persistence fails