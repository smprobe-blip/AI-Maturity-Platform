"""Lead Service for managing leads in Baserow."""
import requests
from typing import List, Dict, Any, Optional
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class LeadService:
    """Service for managing leads via Baserow API."""
    def __init__(self):
        self.baserow_url = "http://baserow:80"
        self.api_token = getattr(settings, 'baserow_api_token', None)
        self.table_id = getattr(settings, 'baserow_leads_table_id', None)

    def _get_headers(self, json_content: bool = False) -> dict:
        """Get headers with correct Host for Baserow."""
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Host": "localhost:3001"
        }
        if json_content:
            headers["Content-Type"] = "application/json"
        return headers

    def _normalize_lead(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация полей Baserow к формату фронтенда."""
        def get_val(*keys):
            for k in keys:
                if k in row:
                    return row[k]
            return None

        score = get_val("Балл зрелости", "composite_score", "Composite Score")
        roi = get_val("ROI Estimate", "roi_estimate")

        return {
            "id": row.get("id"),
            "audit_id": str(get_val("Audit ID", "audit_id") or ""),
            "name": str(get_val("Имя", "name", "Name") or ""),
            "email": str(get_val("Email", "email") or ""),
            "position": str(get_val("Должность", "position", "Position") or ""),
            "industry": str(get_val("Отрасль", "industry", "Industry") or ""),
            "company_size": str(get_val("Размер компании", "company_size", "Company Size") or ""),
            "region": str(get_val("Регион", "region", "Region") or ""),
            "composite_score": float(score) if score is not None else 0.0,
            "maturity_level": str(get_val("maturity_level", "Maturity Level") or ""),
            "roi_estimate": float(roi) if roi is not None else 0.0,
            "status": (get_val("Статус", "status", "Status").get("value")
                        if isinstance(get_val("Статус", "status", "Status"), dict)
                        else (get_val("Статус", "status", "Status") or "New")),
                                    "created_at": str(get_val("Дата создания", "created_at") or ""),
                    }

    async def update_lead_status(self, lead_id: int, status: str) -> bool:
        """Обновить статус лида через Baserow API."""
        from app.integrations.baserow_client import BaserowClient

        client = BaserowClient()
        return await client.update_lead_status(lead_id, status)

    def list_leads(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all leads from Baserow."""
        try:
            if not self.api_token or not self.table_id:
                logger.warning("baserow_not_configured")
                return []
            url = f"{self.baserow_url}/api/database/rows/table/{self.table_id}/"
            headers = self._get_headers()
            params = {"size": limit, "user_field_names": "true"}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            raw_results = data.get("results", [])
            # Нормализуем каждую запись
            return [self._normalize_lead(row) for row in raw_results]
        except Exception as e:
            logger.error("list_leads_failed", error=str(e))
            return []

    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new lead in Baserow."""
        try:
            if not self.api_token or not self.table_id:
                logger.warning("baserow_not_configured")
                return None
            url = f"{self.baserow_url}/api/database/rows/table/{self.table_id}/"
            headers = self._get_headers(json_content=True)
            params = {"user_field_names": "true"}
            response = requests.post(url, headers=headers, params=params, json=lead_data, timeout=10)
            response.raise_for_status()
            logger.info("lead_created", lead_id=response.json().get("id"))
            return response.json()
        except Exception as e:
            logger.error("create_lead_failed", error=str(e), lead_data=lead_data)
            return None

    def get_status(self) -> dict:
        """Get lead service status."""
        return {
            "baserow_url": self.baserow_url,
            "configured": bool(self.api_token and self.table_id),
            "api_token_set": bool(self.api_token),
            "table_id_set": bool(self.table_id)
        }

lead_service = LeadService()