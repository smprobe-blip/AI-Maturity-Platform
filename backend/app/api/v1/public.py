"""Public API routes — express calculator (lead magnet)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.models.audit import AuditExpressCreate, AuditExpressResponse
from app.services.audit_service import AuditService
from app.services.email_service import EmailService

router = APIRouter()


class EmailRequest(BaseModel):
    """Email request model."""
    email: EmailStr


@router.post("/audits/express", response_model=AuditExpressResponse, status_code=status.HTTP_201_CREATED)
async def create_express_audit(data: AuditExpressCreate):
    """Create express audit (public calculator)."""
    import structlog
    logger = structlog.get_logger()
    
    service = AuditService()
    
    try:
        audit_data = service.create_express_audit(data)
        logger.info("audit_created", audit_id=audit_data["audit_id"])
        
        # Sync to Baserow CRM
        try:
            from app.integrations.baserow_client import BaserowClient
            logger.info("starting_baserow_sync", audit_id=audit_data["audit_id"])
            
            baserow = BaserowClient()
            logger.info("baserow_client_config", 
                       url=baserow.api_url, 
                       table_id=baserow.leads_table_id,
                       token_len=len(baserow.api_token))
            
            result = await baserow.sync_lead(audit_data)
            logger.info("baserow_sync_result", result=result)
        except Exception as e:
            logger.error("baserow_sync_error", error=str(e), exc_info=True)
        
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
        
        # Send email (PDF generation would go here)
        success = email_service.send_audit_report(
            to_email=request.email,
            audit_id=audit_id,
            pdf_path=None,  # PDF generation not implemented yet
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
                detail=f"Audit not found: {str(e)}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error: {str(e)}",
            )



@router.get("/benchmarks/{industry}")
async def get_industry_benchmark(industry: str):
    """Get industry benchmark data."""
    # TODO: Implement benchmark retrieval from Parquet storage
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