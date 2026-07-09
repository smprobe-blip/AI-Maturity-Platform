"""Public API routes — express calculator (lead magnet)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import structlog

from app.models.audit import AuditExpressCreate, AuditExpressResponse
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.services.lead_service import lead_service

logger = structlog.get_logger()
router = APIRouter()


class EmailRequest(BaseModel):
    """Email request model."""
    email: EmailStr


@router.post("/audits/express", response_model=AuditExpressResponse, status_code=status.HTTP_201_CREATED)
async def create_express_audit(data: AuditExpressCreate):
    """Create express audit (public calculator)."""
    service = AuditService()
    
    try:
        audit_data = service.create_express_audit(data)
        logger.info("audit_created", audit_id=audit_data["audit_id"])
        
        # === Автоматическое создание лида в Baserow ===
        try:
            calculated_indices = audit_data.get("calculated_indices", {})
            company_profile = audit_data.get("company_profile", {})
            contact = audit_data.get("contact", {})
            
            lead_data = {
                "audit_id": audit_data["audit_id"],
                "name": contact.get("name", "Unknown"),
                "email": contact.get("email", ""),
                "position": contact.get("position", ""),
                "industry": company_profile.get("industry", ""),
                "company_size": company_profile.get("company_size", ""),
                "region": company_profile.get("region", ""),
                "composite_score": float(calculated_indices.get("composite_score", 0.0)),
                "maturity_level": calculated_indices.get("maturity_level", ""),
                "roi_estimate": float(calculated_indices.get("roi_estimate_percent", 0.0)),
                "status": "New",
                "created_at": audit_data.get("created_at", ""),
            }
            
            logger.info("creating_lead", audit_id=audit_data["audit_id"])
            lead_result = lead_service.create_lead(lead_data)
            
            if lead_result:
                logger.info("lead_created_from_audit", 
                           audit_id=audit_data["audit_id"], 
                           lead_id=lead_result.get("id"))
            else:
                logger.warning("lead_creation_failed", audit_id=audit_data["audit_id"])
        except Exception as lead_error:
            # Не блокируем создание аудита из-за ошибки лида
            logger.error("lead_creation_error", 
                        audit_id=audit_data["audit_id"], 
                        error=str(lead_error), 
                        exc_info=True)
        # === КОНЕЦ БЛОКА СОЗДАНИЯ ЛИДА ===
        
        return AuditExpressResponse(
            audit_id=audit_data["audit_id"],
            created_at=audit_data["created_at"],
            calculated_indices=audit_data["calculated_indices"],
            message="Аудит успешно завершён! Отчёт отправлен на вашу почту.",
        )
    
    except Exception as e:
        logger.error("audit_creation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit: {str(e)}",
        )


@router.get("/audits/{audit_id}")
async def get_audit(audit_id: str):
    """Get audit by ID."""
    service = AuditService()
    
    try:
        audit = service.get_audit(audit_id)
        return audit
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit not found: {str(e)}",
        )


@router.post("/audits/{audit_id}/email")
async def send_audit_report(audit_id: str, request: EmailRequest):
    """Send audit report to email."""
    service = AuditService()
    email_service = EmailService()

    try:
        # Get audit
        audit = service.get_audit(audit_id)
        
        # Extract data from audit (correct structure)
        contact = audit.get("contact", {})
        company_profile = audit.get("company_profile", {})
        calculated_indices = audit.get("calculated_indices", {})
        
        # Form company name from contact or industry
        company_name = contact.get("name", "Unknown")
        if not company_name or company_name == "Unknown":
            industry = company_profile.get("industry", "Unknown Industry")
            region = company_profile.get("region", "Unknown Region")
            company_name = f"{industry} - {region}"
        
        score = calculated_indices.get("composite_score", 0.0)
        level = calculated_indices.get("maturity_level", "N/A")

        # Send email
        success = email_service.send_audit_report(
            to_email=request.email,
            company_name=company_name,
            score=score,
            level=level,
            audit_id=audit_id,
        )

        if success:
            return {"message": "Report sent successfully", "email": request.email}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email",
            )

    except HTTPException:
        raise
    except Exception as e:
        # Check if it's "audit not found" error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit {audit_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/benchmarks/{industry}")
async def get_industry_benchmark(industry: str):
    """Get industry benchmark data."""
    return {
        "industry": industry,
        "average_score": 2.8,
        "median_score": 2.7,
        "sample_size": 150,
        "percentiles": {
            "25": 2.1,
            "50": 2.7,
            "75": 3.4,
        },
    }

