"""JSON file storage for audit data."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from app.core.config import settings
from app.core.exceptions import (
    AuditNotFoundException,
    StorageException,
)

logger = structlog.get_logger()


class JSONStorage:
    """Storage for JSON audit files."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.raw_audits_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_audit_path(self, audit_id: str) -> Path:
        """Get path for audit JSON file."""
        year = datetime.now().year
        year_path = self.base_path / str(year)
        year_path.mkdir(parents=True, exist_ok=True)
        return year_path / f"audit_{audit_id}.json"

    def save_audit(self, audit_data: Dict[str, Any]) -> str:
        """Save audit data to JSON file."""
        audit_id = audit_data.get("audit_id")
        if not audit_id:
            raise StorageException("save_audit", {"error": "audit_id is required"})

        file_path = self._get_audit_path(audit_id)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(audit_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info("audit_saved", audit_id=audit_id, path=str(file_path))
            return str(file_path)

        except Exception as e:
            logger.error("audit_save_failed", audit_id=audit_id, error=str(e))
            raise StorageException("save_audit", {"audit_id": audit_id, "error": str(e)})

    def load_audit(self, audit_id: str) -> Dict[str, Any]:
        """Load audit data from JSON file."""
        file_path = self._get_audit_path(audit_id)

        if not file_path.exists():
            raise AuditNotFoundException(audit_id)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info("audit_loaded", audit_id=audit_id)
            return data

        except Exception as e:
            logger.error("audit_load_failed", audit_id=audit_id, error=str(e))
            raise StorageException("load_audit", {"audit_id": audit_id, "error": str(e)})

    def list_audits(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List all audits with optional filters. Recursively searches subdirectories."""
        audits = []

        # Рекурсивный поиск по всем подпапкам (включая года: 2026, 2027, ...)
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith(".json"):
                    filepath = Path(root) / filename
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            audit = json.load(f)
                            audits.append(audit)
                    except Exception as e:
                        logger.error("failed_to_load_audit", filepath=str(filepath), error=str(e))

        # Применяем фильтры
        if filters:
            audits = self._apply_filters(audits, filters)

        # Сортируем по дате создания (новые сверху)
        audits.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # Пагинация
        audits = audits[offset : offset + limit]

        return audits

    def _apply_filters(
        self, audits: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to audit list."""
        result = []
        for audit in audits:
            match = True
            profile = audit.get("company_profile", {})

            for key, value in filters.items():
                if key == "industry" and profile.get("industry") != value:
                    match = False
                    break
                if key == "company_size" and profile.get("company_size") != value:
                    match = False
                    break
                if key == "status" and audit.get("status") != value:
                    match = False
                    break

            if match:
                result.append(audit)

        return result
