"""Baserow CRM client for lead management."""

from typing import Any, Dict, Optional

import requests
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class BaserowClient:
    """Client for self-hosted Baserow CRM."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        leads_table_id: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.BASEROW_URL).rstrip("/")
        self.api_token = api_token or settings.BASEROW_API_TOKEN
        self.leads_table_id = leads_table_id or settings.BASEROW_LEADS_TABLE_ID
        
        # Используем user_field_names=true для работы с именами полей
        self.api_url = f"{self.base_url}/api/database/rows/table/{self.leads_table_id}/?user_field_names=true"

    async def sync_lead(self, audit_data: Dict[str, Any]) -> Optional[int]:
        """Sync audit lead to Baserow CRM."""
        try:
            contact = audit_data.get("contact", {})
            profile = audit_data.get("company_profile", {})
            indices = audit_data.get("calculated_indices", {})

            # Ensure numeric fields are never None
            composite_score = indices.get("composite_score")
            if composite_score is None:
                composite_score = 0.0

            roi_estimate = indices.get("roi_estimate_percent")
            if roi_estimate is None:
                roi_estimate = 0.0

            # Replace em dash with regular dash
            maturity_level = indices.get("maturity_level") or ""
            maturity_level = maturity_level.replace("\u2014", "-").replace("—", "-")

            # Реальные поля таблицы «Лиды из аудита» (RU, user_field_names)
            from app.services.pdf_service import get_industry, get_size

            row_data = {
                "Имя": contact.get("name") or "",
                "Email": contact.get("email") or "",
                "Audit ID": audit_data.get("audit_id") or "",
                "Отрасль": get_industry(audit_data),
                "Размер компании": get_size(audit_data),
                "Балл зрелости": round(float(composite_score), 1),
                "Уровень зрелости": maturity_level,
                "Статус": "New",
                "Источник": audit_data.get("source") or "direct",
                "Дата создания": str(audit_data.get("created_at") or "")[:10],
            }

            logger.info("baserow_sync_attempt",
                       url=self.api_url,
                       audit_id=audit_data.get("audit_id"),
                       row_data=row_data)

            # Используем requests с явной UTF-8 кодировкой
            response = requests.post(
                self.api_url,
                json=row_data,
                headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Host": "localhost:3001",
                },
                timeout=10,
            )

            logger.info("baserow_response",
                       status=response.status_code,
                       body=response.text[:500])

            if response.status_code in (200, 201):
                row_id = response.json().get("id")
                logger.info("lead_synced", row_id=row_id, audit_id=audit_data.get("audit_id"))
                return row_id
            else:
                logger.error("lead_sync_failed",
                           status=response.status_code,
                           body=response.text)
                return None

        except Exception as e:
            logger.error("baserow_sync_error", error=str(e), exc_info=True)
            return None

    async def update_lead_status(self, row_id: int, status: str) -> bool:
        """Update lead status in Baserow."""
        try:
            url = f"{self.base_url}/api/database/rows/table/{self.leads_table_id}/{row_id}/?user_field_names=true"
            response = requests.patch(
                url,
                json={"Статус": status},
                 headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Host": "localhost:3001",
                },
                timeout=10,
            )
            return response.status_code == 200

        except Exception as e:
            logger.error("baserow_update_error", error=str(e))
            return False

    async def get_leads(self, limit: int = 100) -> list:
        """Get leads from Baserow."""
        try:
            url = f"{self.api_url}&size={limit}"
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Host": "localhost:3001",
                },
                timeout=10,
            )
            if response.status_code == 200:
                return response.json().get("results", [])
            return []

        except Exception as e:
            logger.error("baserow_get_leads_error", error=str(e))
            return []
