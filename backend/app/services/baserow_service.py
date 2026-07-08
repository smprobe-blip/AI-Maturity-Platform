"""Baserow CRM integration service."""

from typing import Any, Dict, Optional

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class BaserowService:
    """Service for syncing leads to Baserow CRM."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        table_id: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.baserow_url).rstrip("/")
        self.api_token = api_token or settings.baserow_api_token
        self.table_id = table_id or settings.baserow_leads_table_id
    
    async def sync_lead(self, audit_data: Dict[str, Any]) -> Optional[int]:
        """Sync audit lead to Baserow."""
        if not self.api_token or self.api_token == "your-baserow-api-token":
            logger.warning("baserow_not_configured_skipping_sync")
            return None
        
        # Prepare row data
        row_data = {
            "Audit ID": audit_data.get("audit_id", ""),
            "Industry": audit_data.get("company_profile", {}).get("industry", ""),
            "Company Size": audit_data.get("company_profile", {}).get("company_size", ""),
            "Region": audit_data.get("company_profile", {}).get("region", ""),
            "Email": audit_data.get("contact", {}).get("email", ""),
            "Name": audit_data.get("contact", {}).get("name", ""),
            "Position": audit_data.get("contact", {}).get("position", ""),
            "Maturity Score": audit_data.get("calculated_indices", {}).get("composite_score", 0),
            "Maturity Level": audit_data.get("calculated_indices", {}).get("maturity_level", ""),
            "Created At": audit_data.get("created_at", ""),
            "Status": "New Lead",
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/database/rows/table/{self.table_id}/",
                    headers={
                        "Authorization": f"Token {self.api_token}",
                        "Content-Type": "application/json",
                    },
                    json=row_data,
                )
                
                if response.status_code in (200, 201):
                    result = response.json()
                    logger.info("baserow_lead_synced", row_id=result.get("id"))
                    return result.get("id")
                else:
                    logger.error(
                        "baserow_sync_failed",
                        status_code=response.status_code,
                        response=response.text,
                    )
                    return None
        
        except httpx.RequestError as e:
            logger.error("baserow_request_error", error=str(e))
            return None
    
    async def update_lead_status(self, row_id: int, status: str) -> bool:
        """Update lead status in Baserow."""
        if not self.api_token:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/database/rows/table/{self.table_id}/{row_id}/",
                    headers={
                        "Authorization": f"Token {self.api_token}",
                        "Content-Type": "application/json",
                    },
                    json={"Status": status},
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("baserow_update_failed", error=str(e))
            return False