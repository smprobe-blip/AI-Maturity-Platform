"""Public API endpoints for entry calculator.
Priority 1 + 2.1: 35 questions, benchmark loading, upsell.
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    AuditResponse,
    BenchmarkResponse,
    EmailReportRequest,
    ExpressAuditRequest,
)
from app.services.audit_service import AuditService
from app.services.radar_service import load_benchmark
import structlog

logger = structlog.get_logger()

# ВАЖНО: prefix НЕ указываем здесь — он добавляется в main.py
router = APIRouter(tags=["public"])

_audit_service = AuditService()


@router.post(
    "/audits/express",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create express audit (35 questions)",
)
async def create_express_audit(req: ExpressAuditRequest) -> AuditResponse:
    """Create new express maturity audit.
    
    Accepts nested responses (35 questions) or flat format (7 scores).
    Auto-loads industry benchmark from benchmarks.json.
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
    
    # Email service is optional (may not be configured)
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        success = email_service.send_report(req.email, audit_id, body)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": {"code": "EMAIL_SEND_FAILED"}},
            )
    except ImportError:
        logger.warning("email_service_not_available")
    
    return {"status": "accepted", "message": "Report queued for delivery"}


@router.get(
    "/benchmarks/{industry}",
    summary="Get industry benchmark",
)
async def get_benchmark(industry: str) -> dict:
    """Get industry benchmark data from benchmarks.json.
    
    Returns dimension scores for the specified industry.
    """
    benchmark = load_benchmark(industry)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "BENCHMARK_NOT_FOUND", "message": f"Benchmark for {industry} not found"}},
        )
    
    return {
        "industry": industry,
        "dimension_scores": benchmark,
        "source": "benchmarks.json",
    }