"""Admin API routes — back-office for managing audits, users, exports."""

from typing import List, Optional

from fastapi import APIRouter, Query, Depends

from typing import Optional

from app.core.auth import get_current_user, User
from app.core.config import settings

from fastapi.responses import Response, FileResponse

from app.services.reports.pdf_service import pdf_service

from app.services.email_service import email_service

from app.services.lead_service import lead_service

from app.services.analytics_service import analytics_service
from app.services.export_service import ExportService
from app.analytics.unified_service import UnifiedAnalyticsService
from app.analytics.report_generator import DissertationReportGenerator

from pathlib import Path as FsPath
from datetime import datetime as _dt

_export_service = ExportService()


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


@router.delete("/audits/{audit_id}")
async def delete_audit(audit_id: str):
    """Безвозвратно удалить аудит (для тестовых: source=test_manual) + связанный лид CRM."""
    from app.services.audit_service import AuditService

    service = AuditService()
    try:
        result = service.delete_audit(audit_id)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Audit not found: {str(e)}")

    lead_deleted = False
    try:
        from app.integrations.baserow_client import BaserowClient
        lead_deleted = BaserowClient().delete_lead_by_audit(audit_id)
    except Exception:
        pass

    audit = result.get("audit") or {}
    source = audit.get("source") or (audit.get("request") or {}).get("source")
    return {
        "status": "deleted",
        "audit_id": audit_id,
        "source": source,
        "lead_deleted": lead_deleted,
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
    
    # AuditService возвращает pydantic-модель — сервис PDF ждёт dict
    audit_data = (
        audit.model_dump() if hasattr(audit, "model_dump")
        else audit.dict() if hasattr(audit, "dict")
        else audit
    )

    # Генерируем PDF
    pdf_bytes = pdf_service.generate_audit_report(audit_data)

    company_name = (audit_data.get("company_profile") or {}).get("company_name", "report")
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
async def list_benchmarks(current_user: User = Depends(get_current_user)):
    """Сводка бенчмарков по отраслям (расчёт + ручные правки)."""
    from app.services.benchmark_service import benchmark_service

    return {"items": benchmark_service.admin_summary()}


@router.post("/benchmarks/recalculate")
async def recalculate_benchmarks(current_user: User = Depends(get_current_user)):
    """Пересчитать бенчмарки по накопленным аудитам."""
    from app.services.benchmark_service import benchmark_service

    benchmark_service.clear_cache()
    return {"items": benchmark_service.admin_summary(), "recalculated": True}


@router.put("/benchmarks/{industry}")
async def update_benchmark(industry: str, payload: dict, current_user: User = Depends(get_current_user)):
    """Ручная правка сводки бенчмарка по отрасли (persist в data_storage)."""
    from app.services.settings_overrides import save_benchmark_override

    allowed = {"mean_score", "median_score", "std_dev", "percentile_25", "percentile_75", "sample_size"}
    values = {k: v for k, v in (payload or {}).items() if k in allowed}
    saved = save_benchmark_override(industry, values)
    from app.services.benchmark_service import benchmark_service
    benchmark_service.clear_cache()
    return {"industry": industry, "saved": saved.get(industry, {})}


@router.put("/settings/weights")
async def update_weights(payload: dict, current_user: User = Depends(get_current_user)):
    """Базовые веса осей методики ('1'..'7'). Нормализуются, клампятся алгоритмом А.1-А.2."""
    from app.services.settings_overrides import save_overrides, load_overrides
    from app.services.industry_weights_service import _clamp_normalize

    weights = (payload or {}).get("weights")
    if not isinstance(weights, dict) or set(weights.keys()) != {str(i) for i in range(1, 8)}:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="weights: ровно ключи '1'..'7'")
    try:
        weights = {k: float(v) for k, v in weights.items()}
        if any(v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
            raise ValueError
    except (TypeError, ValueError):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="weights: положительные числа")
    normalized = _clamp_normalize(weights)
    saved = save_overrides({"dimension_weights": normalized}, ["dimension_weights"])
    return {"saved": saved.get("dimension_weights")}


@router.delete("/settings/weights")
async def reset_weights(current_user: User = Depends(get_current_user)):
    """Сбросить веса осей к базовым (гл. 2.10)."""
    from app.services.settings_overrides import load_overrides, save_overrides
    from app.services.industry_weights_service import BASE_WEIGHTS

    current = load_overrides()
    current.pop("dimension_weights", None)
    allowed = ["public_base_url", "postbox_from_email", "postbox_from_name", "dimension_weights"]
    save_overrides(current, allowed)
    return {"saved": BASE_WEIGHTS, "reset": True}


@router.put("/settings")
async def update_settings(payload: dict, current_user: User = Depends(get_current_user)):
    """Редактируемые настройки (белый список, persist в data_storage)."""
    from app.services.settings_overrides import save_overrides

    allowed = ["public_base_url", "postbox_from_email", "postbox_from_name"]
    saved = save_overrides(payload or {}, allowed)
    return {
        "saved": {k: saved[k] for k in allowed if k in saved},
        "message": "Настройки сохранены",
    }

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


@router.patch("/leads/{lead_id}/status")
async def update_lead_status(lead_id: int, status_data: dict):
    """Обновить статус лида в Baserow."""
    status = (status_data or {}).get("status")
    if not status:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="status is required")

    result = await lead_service.update_lead_status(lead_id, status)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to update lead status")
    return {"id": lead_id, "status": status}


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

# === Users (респонденты платформы) ===
@router.get("/users")
async def list_users(current_user: User = Depends(get_current_user)):
    """Пользователи платформы: агрегация респондентов по email из аудитов."""
    from app.services.audit_service import AuditService

    items = AuditService().list_audits()
    users: dict = {}
    for a in items:
        contact = a.get("contact") or {}
        email = (contact.get("email") or "").strip().lower()
        if not email or "@" not in email:
            continue
        u = users.setdefault(email, {
            "email": email,
            "name": contact.get("name") or "",
            "audits_count": 0,
            "test_audits": 0,
            "first_seen": a.get("created_at") or "",
            "last_seen": a.get("created_at") or "",
            "sources": set(),
        })
        u["audits_count"] += 1
        if a.get("source") == "test_manual":
            u["test_audits"] += 1
        created = a.get("created_at") or ""
        if created:
            u["first_seen"] = min(u["first_seen"], created)
            u["last_seen"] = max(u["last_seen"], created)
        src = a.get("source") or (a.get("request") or {}).get("source")
        if src:
            u["sources"].add(src)
    out = []
    for u in users.values():
        u["sources"] = sorted(u["sources"])
        out.append(u)
    out.sort(key=lambda x: x["last_seen"], reverse=True)
    return {"items": out, "total": len(out)}


# === Операторы (Keycloak) ===
@router.get("/users/keycloak")
async def list_keycloak_users(current_user: User = Depends(get_current_user)):
    """Операторы платформы: пользователи realm Keycloak."""
    from app.integrations.keycloak_client import KeycloakClient

    items = await KeycloakClient().list_users()
    return {"items": items, "total": len(items)}


@router.post("/users/invite")
async def invite_operator(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """Создать оператора в Keycloak: пользователь + временный пароль (показывается один раз)."""
    from app.integrations.keycloak_client import KeycloakClient

    email = (payload or {}).get("email", "").strip().lower()
    if not email or "@" not in email:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="email is required")
    role = (payload or {}).get("role", "analyst")
    send_email = bool((payload or {}).get("send_email"))
    required_actions = ["VERIFY_EMAIL", "UPDATE_PASSWORD"] if send_email else None
    result = await KeycloakClient().create_user(
        email=email,
        first_name=(payload or {}).get("first_name", ""),
        last_name=(payload or {}).get("last_name", ""),
        roles=[role],
        required_actions=required_actions,
    )
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Не удалось создать пользователя в Keycloak")
    return {
        "user_id": result["user_id"],
        "email": email,
        "role": role,
        "email_sent": result.get("email_sent", False),
        "temp_password": result.get("temp_password"),
    }


@router.delete("/users/keycloak/{user_id}")
async def delete_keycloak_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Удалить оператора из Keycloak."""
    from app.integrations.keycloak_client import KeycloakClient

    if current_user and getattr(current_user, "sub", "") == user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Нельзя удалить свою учётную запись")
    ok = await KeycloakClient().delete_user(user_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted", "user_id": user_id}


# === Почта Keycloak (для execute-actions-email) ===
@router.get("/users/keycloak-smtp")
async def get_keycloak_smtp(current_user: User = Depends(get_current_user)):
    from app.integrations.keycloak_client import KeycloakClient

    return await KeycloakClient().get_realm_smtp()


@router.put("/users/keycloak-smtp")
async def set_keycloak_smtp(payload: dict, current_user: User = Depends(get_current_user)):
    from app.integrations.keycloak_client import KeycloakClient

    data = payload or {}
    required = ["host", "from"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Требуются поля: {', '.join(missing)}")
    smtp = {
        "host": data["host"],
        "port": str(data.get("port", "587")),
        "from": data["from"],
        "fromDisplayName": data.get("from_display_name", "AI Maturity Platform"),
        "ssl": "true" if data.get("ssl") else "false",
        "starttls": "true" if data.get("starttls", True) else "false",
        "auth": "true" if data.get("auth") else "false",
        "user": data.get("user", ""),
        "password": data.get("password", ""),
    }
    if not smtp["auth"]:
        smtp.pop("user", None)
        smtp.pop("password", None)
    ok = await KeycloakClient().set_realm_smtp(smtp)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Не удалось сохранить SMTP в Keycloak")
    return {"status": "saved"}


# === Настройки (не-секретный снимок) ===
@router.get("/settings")
async def get_settings(current_user: User = Depends(get_current_user)):
    """Сводка состояния платформы: интеграции, данные. Секреты не возвращаются."""
    from app.core.config import settings as app_settings
    from app.services.audit_service import AuditService

    audits = AuditService().list_audits()
    active = [a for a in audits if a.get("status") != "archived"]
    archived_count = len(audits) - len(active)
    test_manual = sum(
        1 for a in audits
        if (a.get("source") or (a.get("request") or {}).get("source")) == "test_manual"
    )
    reports_dir = FsPath(app_settings.reports_path) / "dissertation"
    reports_count = len(list(reports_dir.glob("*.pdf"))) if reports_dir.exists() else 0

    from app.services.industry_weights_service import get_industry_weights

    eff_weights, w_source = get_industry_weights()
    return {
        "weights": {"values": eff_weights, "source": w_source},
        "platform": {"name": "AI Maturity Assessment Platform"},
        "integrations": {
            "keycloak": {
                "realm": app_settings.keycloak_realm,
                "client_id": app_settings.keycloak_client_id,
                "configured": True,
            },
            "baserow": {
                "url": app_settings.BASEROW_URL,
                "leads_table_id": app_settings.BASEROW_LEADS_TABLE_ID,
                "configured": bool(app_settings.BASEROW_API_TOKEN),
            },
            "email": email_service.get_status(),
        },
        "data": {
            "audits_total": len(audits),
            "audits_active": len(active),
            "audits_archived": archived_count,
            "audits_test_manual": test_manual,
            "reports_pdf": reports_count,
        },
    }


# === Журнал аудитов ===
@router.get("/audit-log")
async def get_audit_log(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(200, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Хронология создания аудитов платформой (из хранилища, новые сверху)."""
    from app.services.audit_service import AuditService

    items = AuditService().list_audits()
    events = []
    for a in items:
        req = a.get("request") or {}
        email = (a.get("contact") or {}).get("email") or req.get("contact_email") or "—"
        events.append({
            "timestamp": a.get("created_at"),
            "user_email": email,
            "action": "audit.created",
            "resource_type": "audit",
            "resource_id": a.get("audit_id"),
            "source": a.get("source") or req.get("source") or "",
            "status": a.get("status") or "completed",
            "success": (a.get("status") or "completed") != "failed",
        })
    events.sort(key=lambda e: e["timestamp"] or "", reverse=True)
    if user_id:
        events = [e for e in events if user_id.lower() in (e["user_email"] or "").lower()]
    if action:
        events = [e for e in events if e["action"] == action]
    return {"items": events[:limit]}


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


# ─── Выгрузки ───


@router.post("/exports")
async def create_export(payload: dict, current_user: User = Depends(get_current_user)):
    """Создать выгрузку данных (экспорт в файл)."""
    return _export_service.create_export(
        export_type=payload.get("export_type", "audits_aggregated"),
        format=payload.get("format", "csv"),
        filters=payload.get("filters"),
        nda_signed=bool(payload.get("nda_signed", False)),
        user_id=current_user.sub,
    )


@router.get("/exports/history")
async def get_exports_history(limit: int = 50, current_user: User = Depends(get_current_user)):
    """История выгрузок."""
    return _export_service.get_export_history(limit)


@router.get("/exports/{export_id}/download")
async def download_export_file(export_id: str, current_user: User = Depends(get_current_user)):
    """Скачать файл выгрузки."""
    from fastapi import HTTPException

    path = _export_service.get_export_file_path(export_id)
    if not path:
        raise HTTPException(status_code=404, detail="Export file not found")
    return FileResponse(str(path), filename=path.name)


# ─── Отчеты (библиотека) ───


@router.get("/reports")
async def list_report_files(current_user: User = Depends(get_current_user)):
    """Библиотека сгенерированных PDF-отчетов."""
    base = FsPath(settings.reports_path)
    items = []
    if base.exists():
        for f in sorted(base.rglob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True):
            items.append({
                "filename": f.name,
                "kind": "dissertation" if "dissertation" in str(f.parent) else "audit",
                "size_bytes": f.stat().st_size,
                "created_at": _dt.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    return {"items": items}


@router.get("/reports/download/{filename}")
async def download_report_file(filename: str, current_user: User = Depends(get_current_user)):
    """Скачать PDF-отчет по имени файла."""
    from fastapi import HTTPException

    safe = FsPath(filename).name
    base = FsPath(settings.reports_path)
    matches = list(base.rglob(safe))
    if not matches:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(str(matches[0]), filename=safe)


@router.post("/reports/generate-dissertation")
async def generate_dissertation_report(current_user: User = Depends(get_current_user)):
    """Сгенерировать диссертационный отчет (полный статистический анализ)."""
    analytics_data = UnifiedAnalyticsService().run_full_analysis()
    path = DissertationReportGenerator().generate_full_report(analytics_data)
    return {"filename": FsPath(path).name, "path": str(path)}


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
