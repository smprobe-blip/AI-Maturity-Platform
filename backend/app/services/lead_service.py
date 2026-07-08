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
            "Host": "localhost:3001"  # Required by Baserow (BASEROW_PUBLIC_URL)
        }
        if json_content:
            headers["Content-Type"] = "application/json"
        return headers
    
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
            return data.get("results", [])
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
