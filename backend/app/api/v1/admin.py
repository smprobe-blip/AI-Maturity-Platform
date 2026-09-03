"""Admin API routes — back-office for managing audits, users, exports."""

from typing import List, Optional

from fastapi import APIRouter, Query, Depends

from typing import Optional

from app.core.auth import get_current_user, User

from fastapi.responses import Response

from app.services.reports.pdf_service import pdf_service

from app.services.email_service import email_service

from app.services.lead_service import lead_service

from app.services.analytics_service import analytics_service


router = APIRouter()


@router.get("/audits")
async def list_audits(
    industry: Optional[str] = None,
    company_size: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
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
    
    # Полный отфильтрованный список (с поиском), затем пагинация
    audits = service.list_audits(filters=filters if filters else None, search=search, limit=0, offset=0)
    total = len(audits)
    total_pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": audits[offset:offset + limit],
        "total": total,
        "page": offset // limit + 1,
        "page_size": limit,
        "total_pages": total_pages,
    }


@router.get("/audits/{audit_id}")
async def get_audit(audit_id: str):
    """Get audit details (enriched: raw_responses, contact, status)."""
    from app.services.audit_service import AuditService

    service = AuditService()
    try:
        return service.get_audit_detail(audit_id)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Audit not found: {str(e)}")

from app.services.dashboard_service import DashboardService

_dashboard_service = DashboardService()


@router.get("/dashboard/business")
async def get_business_dashboard():
    """Get business metrics dashboard."""
    return _dashboard_service.get_business_metrics()


@router.get("/dashboard/scientific")
async def get_scientific_dashboard():
    """Get scientific/research metrics dashboard."""
    return _dashboard_service.get_scientific_metrics()


@router.get("/dashboard/operations")
async def get_operations_dashboard():
    """Get operations metrics dashboard."""
    return _dashboard_service.get_operational_metrics()


@router.get("/dashboard/quality")
async def get_quality_dashboard():
    """Get quality metrics dashboard."""
    return _dashboard_service.get_quality_metrics()


@router.post("/audits/{audit_id}/archive")
async def archive_audit(audit_id: str):
    """Пометить аудит архивным."""
    from app.services.audit_service import AuditService

    service = AuditService()
    try:
        return service.archive_audit(audit_id)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Audit not found: {str(e)}")


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

# === Analytics Endpoints ===

@router.get("/analytics/overview")
async def get_analytics_overview(current_user: User = Depends(get_current_user)):
    """Get analytics overview."""
    return analytics_service.get_overview()


@router.get("/analytics/by-industry")
async def get_analytics_by_industry(current_user: User = Depends(get_current_user)):
    """Get analytics grouped by industry."""
    return analytics_service.get_by_industry()


@router.get("/analytics/by-level")
async def get_analytics_by_level(current_user: User = Depends(get_current_user)):
    """Get analytics grouped by maturity level."""
    return analytics_service.get_by_level()


@router.get("/analytics/top-companies")
async def get_analytics_top_companies(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get top companies by composite score."""
    return analytics_service.get_top_companies(limit)

@router.get("/analytics/by-company-size")
async def get_analytics_by_company_size(current_user: User = Depends(get_current_user)):
    """Get analytics grouped by company size."""
    return analytics_service.get_by_company_size()


@router.get("/research/export-csv", summary="Export research dataset (CSV)")
async def export_research_csv(token: str = ""):
    """Export item-level dataset (35 answers + metadata) for statistical analysis."""
    import csv, io, json, os
    from pathlib import Path
    from fastapi.responses import Response, JSONResponse

    expected = os.getenv("RESEARCH_EXPORT_TOKEN", "research-dev-token")
    if token != expected:
        return JSONResponse(status_code=403, content={"error": "Invalid token"})

    audits_dir = Path("/data_storage/raw_audits")
    records = []
    qcols = []

    if audits_dir.exists():
        for f in sorted(audits_dir.rglob("audit_*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            req = data.get("request", {}) or {}
            if not req.get("research_consent"):
                continue

            flat = {}
            raw = req.get("responses", {}) or {}
            for k, v in raw.items():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        flat["q%s_%s" % (k, k2)] = v2
                else:
                    flat["q%s" % k] = v
            for k in flat:
                if k not in qcols:
                    qcols.append(k)

            indices = data.get("calculated_indices", {}) or {}
            rec = {
                "audit_id": data.get("audit_id", f.stem),
                "created_at": data.get("created_at", ""),
                "industry": req.get("company_industry", ""),
                "size": req.get("company_size", ""),
                "role": req.get("respondent_role", ""),
                "company": req.get("company_name", ""),
                "source": req.get("source", ""),
                "email": req.get("contact_email", ""),
                "name": req.get("contact_name", ""),
                "composite": indices.get("composite_score", ""),
                "level": indices.get("maturity_level", ""),
            }
            rec.update(flat)
            records.append(rec)

    header = ["audit_id", "created_at", "industry", "size", "role", "company",
              "source", "email", "name", "composite", "level"] + sorted(qcols)
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=header, extrasaction="ignore")
    w.writeheader()
    for rec in records:
        w.writerow(rec)

    return Response(
        content=out.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=research_data.csv"},
    )
