"""Admin API routes — back-office for managing audits, users, exports."""

from typing import List, Optional

from fastapi import APIRouter, Query, Depends

from typing import Optional

from app.core.auth import get_current_user, User

from fastapi.responses import Response

from app.services.reports.pdf_service import pdf_service

from app.services.email_service import email_service

from app.services.lead_service import lead_service


router = APIRouter()


@router.get("/audits")
async def list_audits(
    industry: Optional[str] = None,
    company_size: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),  
):
    """List audits with filters."""
    from app.services.audit_service import AuditService
    
    service = AuditService()
    
    # Собираем фильтры
    filters = {}
    if industry:
        filters["industry"] = industry
    if company_size:
        filters["company_size"] = company_size
    if status:
        filters["status"] = status
    
    # Получаем аудиты
    audits = service.list_audits(filters=filters if filters else None, limit=limit, offset=offset)
    
    # Получаем общее количество для пагинации
    all_audits = service.list_audits(filters=filters if filters else None, limit=10000, offset=0)
    total = len(all_audits)
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": audits,
        "total": total,
        "page": offset // limit + 1,
        "page_size": limit,
        "total_pages": total_pages,
    }


@router.get("/audits/{audit_id}")
async def get_audit(audit_id: str):
    """Get audit details."""
    from app.services.audit_service import AuditService
    
    service = AuditService()
    try:
        audit = service.get_audit(audit_id)
        return audit
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Audit not found: {str(e)}")

@router.get("/dashboard/business")
async def get_business_dashboard():
    """Get business metrics dashboard."""
    # TODO: Implement with AnalyticsService
    return {
        "total_audits": 0,
        "audits_this_month": 0,
        "conversion_rate": 0.0,
        "average_maturity_score": 0.0,
    }


@router.get("/audits/{audit_id}/report/pdf")
async def get_audit_pdf_report(
    audit_id: str,
    current_user: User = Depends(get_current_user),
):
    """Generate PDF report for an audit."""
    from app.services.audit_service import AuditService
    
    service = AuditService()
    try:
        audit = service.get_audit(audit_id)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Audit not found: {str(e)}")
    
    # Генерируем PDF
    pdf_bytes = pdf_service.generate_audit_report(audit)
    
    company_name = audit.get("company_profile", {}).get("company_name", "report")
    safe_name = "".join(c for c in company_name if c.isalnum() or c in " -_")[:50]
    filename = f"ai_maturity_report_{safe_name}_{audit_id[:8]}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        }
    )

@router.get("/benchmarks")
async def list_benchmarks():
    """List all industry benchmarks."""
    # TODO: Implement with BenchmarkService
    return []


@router.post("/benchmarks/recalculate")
async def recalculate_benchmarks():
    """Recalculate all benchmarks."""
    # TODO: Implement with BenchmarkService
    return {"message": "Benchmarks recalculation started"}

@router.get("/leads")
async def list_leads(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
    """List all leads from Baserow."""
    leads = lead_service.list_leads(limit=limit, offset=offset)
    return {"items": leads, "total": len(leads)}


@router.get("/email/status")
async def get_email_status(
    current_user: User = Depends(get_current_user),
):
    """Get email service status."""
    return email_service.get_status()


@router.get("/leads/status")
async def get_leads_status(
    current_user: User = Depends(get_current_user),
):
    """Get lead service status."""
    return lead_service.get_status()

@router.post("/email/send-test")
async def send_test_email(
    to_email: str = "test@example.com",
    current_user: User = Depends(get_current_user),
):
    """Send test email."""
    success = email_service.send_email(
        to_emails=[to_email],
        subject="Test Email from AI Maturity Platform",
        html_body="""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">Test Email</h2>
            <p>This is a test email from AI Maturity Platform.</p>
            <p>If you receive this, email configuration is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">AI Maturity Platform</p>
        </body>
        </html>
        """
    )
    
    if success:
        return {"status": "success", "message": f"Email sent to {to_email}"}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to send email")
