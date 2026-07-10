"""Audit business logic service.
v1.1 — Priority 1: integrates pattern_service, top-3, upsell.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import structlog
from app.core.config import settings
from app.models.schemas import AuditResponse, ExpressAuditRequest
from app.services.radar_service import (
    DIMENSION_NAMES,
    calculate_indices,
    generate_recommendations,
)

logger = structlog.get_logger()


class AuditService:
    """Service for managing audits."""

    def __init__(self) -> None:
        self.raw_path = Path(str(settings.raw_audits_path))
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def _audit_file(self, audit_id: str, year: Optional[int] = None) -> Path:
        year = year or datetime.now(timezone.utc).year
        year_dir = self.raw_path / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        return year_dir / f"audit_{audit_id}.json"

    def create_express_audit(self, req: ExpressAuditRequest) -> AuditResponse:
        """Create new express audit and persist to JSON."""
        audit_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # Calculate indices (returns tuple with upsell_triggers)
        indices, upsell_triggers = calculate_indices(
            responses=req.responses,
            company_size=req.company_size,
            target_scores=req.target_scores,
            benchmark_scores=None,  # TODO: load from benchmark_service
        )

        # Generate recommendations from top-3 analysis
        recommendations = generate_recommendations(
            dimension_scores=indices.dimension_scores,
            top3_bottlenecks=indices.top3_bottlenecks,
            top3_anchors=indices.top3_anchors,
        )

        # Build raw_responses in new format (35 questions)
        raw_responses = []
        for dim_id, value in req.responses.items():
            if isinstance(value, dict):
                for q_id, score in value.items():
                    raw_responses.append({
                        'dimension_id': dim_id,
                        'dimension_name': DIMENSION_NAMES.get(dim_id, f'Ось {dim_id}'),
                        'question_id': q_id,
                        'score': float(score),
                        'confidence_level': 4,
                    })
            else:
                raw_responses.append({
                    'dimension_id': dim_id,
                    'dimension_name': DIMENSION_NAMES.get(dim_id, f'Ось {dim_id}'),
                    'question_id': 'aggregated',
                    'score': float(value),
                    'confidence_level': 4,
                })

        audit_data = {
            'audit_metadata': {
                'audit_id': audit_id,
                'audit_type': 'express',
                'report_type': req.report_type,
                'created_at': created_at,
                'version': '1.1',
                'methodology_version': 'v5.0',
            },
            'company_profile': {
                'industry': req.company_industry,
                'size': req.company_size,
                'anonymized': True,
            },
            'contact': {
                'email': req.contact_email,
                'name': req.contact_name,
                'pdn_consent': req.pdn_consent,
            },
            'target_scores': req.target_scores,
            'raw_responses': raw_responses,
            'calculated_indices': indices.model_dump(),
            'recommendations': recommendations,
            'upsell_triggers': upsell_triggers,
            'audit_events': [
                {'event': 'created', 'timestamp': created_at}
            ],
        }

        file_path = self._audit_file(audit_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)

        logger.info(
            'audit_created',
            audit_id=audit_id,
            report_type=req.report_type,
            industry=req.company_industry,
            composite=indices.composite_score,
            pattern=indices.pattern.pattern_type if indices.pattern else None,
        )

        return AuditResponse(
            audit_id=audit_id,
            created_at=created_at,
            report_type=req.report_type,
            company_profile=audit_data['company_profile'],
            calculated_indices=indices,
            recommendations=recommendations,
            upsell_triggers=upsell_triggers,
        )

    def get_audit(self, audit_id: str) -> Optional[AuditResponse]:
        """Load audit by ID."""
        for year_dir in self.raw_path.iterdir():
            if not year_dir.is_dir():
                continue
            candidate = year_dir / f"audit_{audit_id}.json"
            if candidate.exists():
                with open(candidate, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                from app.models.schemas import CalculatedIndices, PatternInfo

                idx_data = data['calculated_indices']
                pattern_data = idx_data.get('pattern')
                pattern = PatternInfo(**pattern_data) if pattern_data else None

                indices = CalculatedIndices(
                    composite_score=idx_data['composite_score'],
                    maturity_level=idx_data['maturity_level'],
                    dimension_scores=idx_data['dimension_scores'],
                    roi_estimate_percent=idx_data.get('roi_estimate_percent'),
                    tco_estimate_millions=idx_data.get('tco_estimate_millions'),
                    top3_bottlenecks=idx_data.get('top3_bottlenecks', []),
                    top3_anchors=idx_data.get('top3_anchors', []),
                    pattern=pattern,
                    gap_analysis=idx_data.get('gap_analysis'),
                )

                return AuditResponse(
                    audit_id=data['audit_metadata']['audit_id'],
                    created_at=data['audit_metadata']['created_at'],
                    report_type=data['audit_metadata'].get('report_type', 'express'),
                    company_profile=data['company_profile'],
                    calculated_indices=indices,
                    recommendations=data.get('recommendations', []),
                    upsell_triggers=data.get('upsell_triggers', []),
                )
        return None

    def list_audits(self, limit: int = 100) -> list:
        """List recent audits."""
        audits = []
        for year_dir in sorted(self.raw_path.iterdir(), reverse=True):
            if not year_dir.is_dir():
                continue
            for f in sorted(year_dir.glob('audit_*.json'), reverse=True):
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    audits.append({
                        'audit_id': data['audit_metadata']['audit_id'],
                        'created_at': data['audit_metadata']['created_at'],
                        'report_type': data['audit_metadata'].get('report_type', 'express'),
                        'industry': data['company_profile']['industry'],
                        'size': data['company_profile']['size'],
                        'composite': data['calculated_indices']['composite_score'],
                        'pattern': data['calculated_indices'].get('pattern', {}).get('pattern_type'),
                    })
                    if len(audits) >= limit:
                        return audits
                except Exception as e:
                    logger.warning('audit_load_failed', file=str(f), error=str(e))
        return audits