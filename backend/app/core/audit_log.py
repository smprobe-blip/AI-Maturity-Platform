"""Admin action audit logging."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class AdminAuditLog:
    """Logs all admin actions for compliance and traceability."""

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path or settings.logs_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_path / "admin_actions.json"

    def log_action(
        self,
        user_id: str,
        user_email: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ) -> None:
        """Log an admin action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "success": success,
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            logger.info(
                "admin_action",
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                success=success,
            )
        except Exception as e:
            logger.error("audit_log_write_failed", error=str(e))

    def get_actions(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> list:
        """Retrieve audit log entries."""
        entries = []

        if not self.log_file.exists():
            return entries

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    entry = json.loads(line)

                    if user_id and entry.get("user_id") != user_id:
                        continue
                    if action and entry.get("action") != action:
                        continue

                    entries.append(entry)

            # Sort by timestamp descending, apply limit
            entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return entries[:limit]

        except Exception as e:
            logger.error("audit_log_read_failed", error=str(e))
            return []


# Global instance
audit_log = AdminAuditLog()