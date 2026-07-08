"""Audit log service — log all admin actions."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class AuditLogService:
    """Service for logging admin actions (compliance requirement)."""
    
    def __init__(self, logs_dir: Optional[str] = None):
        self.logs_dir = Path(logs_dir or settings.logs_path)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_dir / "admin_actions.json"
    
    def log_action(
        self,
        user_id: str,
        user_email: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """Log an admin action."""
        event_id = str(uuid.uuid4())
        entry = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        try:
            # Append to JSONL file (one entry per line)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            logger.info(
                "admin_action_logged",
                event_id=event_id,
                action=action,
                resource_type=resource_type,
                user_id=user_id,
            )
            return event_id
        
        except Exception as e:
            logger.error("audit_log_write_failed", error=str(e))
            # Don't raise — logging failure shouldn't block business logic
            return ""
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filters."""
        if not self.log_file.exists():
            return []
        
        entries: List[Dict[str, Any]] = []
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        # Apply filters
                        if user_id and entry.get("user_id") != user_id:
                            continue
                        if action and entry.get("action") != action:
                            continue
                        if resource_type and entry.get("resource_type") != resource_type:
                            continue
                        
                        entries.append(entry)
                    
                    except json.JSONDecodeError:
                        logger.warning("invalid_log_entry_skipped")
                        continue
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return entries[offset : offset + limit]
        
        except Exception as e:
            logger.error("audit_log_read_failed", error=str(e))
            return []