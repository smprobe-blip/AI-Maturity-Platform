"""Public API endpoints for entry calculator.
v1.1 — Priority 1: 35 questions, report_type, target_scores, pdn_consent.
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    AuditResponse,
    BenchmarkResponse,
    EmailReportRequest,
    ExpressAuditRequest,
)
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
import structlog

logger = structlog.get_logger()

# ВАЖНО: prefix НЕ указываем здесь — он добавляется в main.py
router = APIRouter(tags=["public"])

_audit_service = AuditService()
_email_service = EmailService()


@router.post(
    "/audits/express",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create express audit (35 questions)",
)
async def create_express_audit(req: ExpressAuditRequest) -> AuditResponse:
    """Create new express maturity audit.
    
    Accepts nested responses (35 questions) or flat format (7 scores).
    Returns calculated indices with pattern diagnosis, top-3, upsell triggers.
    """
    try:
        return _audit_service.create_express_audit(req)
    except Exception as e:
        logger.error("audit_creation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "AUDIT_CREATION_FAILED", "message": str(e)}},
        )


@router.get(
    "/audits/{audit_id}",
    response_model=AuditResponse,
    summary="Get audit by ID",
)
async def get_audit(audit_id: str) -> AuditResponse:
    """Load existing audit results by ID."""
    audit = _audit_service.get_audit(audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "AUDIT_NOT_FOUND", "message": f"Audit {audit_id} not found"}},
        )
    return audit


@router.post(
    "/audits/{audit_id}/email",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Email audit report",
)
async def email_audit_report(audit_id: str, req: EmailReportRequest) -> dict:
    """Send audit report to specified email."""
    audit = _audit_service.get_audit(audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "AUDIT_NOT_FOUND"}},
        )
    
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш отчёт по оценке ИИ-зрелости готов.\n\n"
        f"ID аудита: {audit_id}\n"
        f"Комплексная оценка: {audit.calculated_indices.composite_score:.2f} / 5.00\n"
        f"Уровень зрелости: {audit.calculated_indices.maturity_level}\n\n"
        f"Рекомендации:\n" +
        "\n".join(f"• {r}" for r in audit.recommendations) +
        f"\n\nОткрыть полную версию: http://localhost:3000/results/{audit_id}\n"
    )
    
    success = _email_service.send_report(req.email, audit_id, body)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "EMAIL_SEND_FAILED"}},
        )
    
    return {"status": "accepted", "message": "Report queued for delivery"}


@router.get(
    "/benchmarks/{industry}",
    response_model=BenchmarkResponse,
    summary="Get industry benchmark",
)
async def get_benchmark(industry: str) -> BenchmarkResponse:
    """Get industry benchmark data.
    
    Returns mean scores and percentiles for the specified industry.
    TODO: Calculate from DuckDB when enough data (min N≥30).
    """
    # Stub — will be replaced by benchmark_service.py in Priority 2
    return BenchmarkResponse(
        industry=industry,
        sample_size=0,
        dimension_means={str(i): 0.0 for i in range(1, 8)},
        composite_mean=0.0,
        composite_median=0.0,
        percentiles={"p25": 0.0, "p50": 0.0, "p75": 0.0},
    )