"""Settings service — methodology weights, integration configs."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()

DEFAULT_METHODOLOGY = {
    "version": "1.0",
    "dimensions": 7,
    "questions_per_dimension": 5,
    "score_range": {"min": 1, "max": 5},
    "weights": {
        "1": 0.15,
        "2": 0.15,
        "3": 0.15,
        "4": 0.15,
        "5": 0.15,
        "6": 0.20,
        "7": 0.05,
    },
    "maturity_levels": {
        "L1": {"min": 0.0, "max": 1.5, "label": "L1 — Initial"},
        "L2": {"min": 1.5, "max": 2.5, "label": "L2 — Developing"},
        "L3": {"min": 2.5, "max": 3.5, "label": "L3 — Defined"},
        "L4": {"min": 3.5, "max": 4.5, "label": "L4 — Managed"},
        "L5": {"min": 4.5, "max": 5.0, "label": "L5 — Optimizing"},
    },
    "anonymization_levels": {
        "L0": "Full data (requires NDA)",
        "L1": "Company name hashed, contact visible",
        "L2": "Only aggregated data",
        "L3": "Fully anonymized benchmarks",
    },
}

DEFAULT_INTEGRATIONS = {
    "baserow": {"enabled": True, "url": "", "table_id": 1},
    "smtp": {"enabled": True, "host": "", "port": 465},
    "yookassa": {"enabled": False, "shop_id": ""},
}


class SettingsService:
    """Service for managing platform settings."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_dir = Path(config_path or settings.data_storage_path) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.methodology_path = self.config_dir / "methodology.json"
        self.integrations_path = self.config_dir / "integrations.json"

    def get_methodology(self) -> Dict[str, Any]:
        """Get current methodology settings."""
        if self.methodology_path.exists():
            try:
                with open(self.methodology_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return DEFAULT_METHODOLOGY.copy()

    def update_methodology(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update methodology settings."""
        current = self.get_methodology()

        # Merge updates
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(current.get(key), dict):
                current[key].update(value)
            else:
                current[key] = value

        # Validate weights sum to 1.0
        if "weights" in updates:
            total = sum(float(v) for v in current["weights"].values())
            if abs(total - 1.0) > 0.01:
                from app.core.exceptions import AppException

                raise AppException(
                    status_code=400,
                    error_code="INVALID_WEIGHTS",
                    message=f"Weights must sum to 1.0, got {total}",
                )

        # Save
        with open(self.methodology_path, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)

        logger.info("methodology_updated", keys=list(updates.keys()))
        return current

    def get_integrations(self) -> Dict[str, Any]:
        """Get integration settings."""
        if self.integrations_path.exists():
            try:
                with open(self.integrations_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return DEFAULT_INTEGRATIONS.copy()

    def update_integrations(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update integration settings."""
        current = self.get_integrations()

        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(current.get(key), dict):
                current[key].update(value)
            else:
                current[key] = value

        with open(self.integrations_path, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)

        logger.info("integrations_updated", keys=list(updates.keys()))
        return current