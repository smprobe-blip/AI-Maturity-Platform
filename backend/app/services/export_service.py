"""Export service — generate data exports in various formats."""

import csv
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog

from app.core.config import settings
from app.core.exceptions import AppException
from app.storage.json_storage import JSONStorage
from app.storage.parquet_storage import ParquetStorage

logger = structlog.get_logger()


class ExportService:
    """Service for generating data exports."""

    def __init__(self):
        self.json_storage = JSONStorage()
        self.parquet_storage = ParquetStorage()
        self.exports_path = Path(settings.exports_path)
        self.exports_path.mkdir(parents=True, exist_ok=True)

    def create_export(
        self,
        export_type: str,
        format: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        user_id: str = "system",
        nda_signed: bool = False,
    ) -> Dict[str, Any]:
        """Create a new data export."""
        export_id = str(uuid.uuid4())
        created_at = datetime.now()

        logger.info(
            "export_started",
            export_id=export_id,
            type=export_type,
            format=format,
            user_id=user_id,
        )

        try:
            # Get data based on export type
            data = self._get_export_data(export_type, filters, nda_signed)

            # Filter columns if specified
            if columns and isinstance(data, pd.DataFrame):
                available_cols = [c for c in columns if c in data.columns]
                data = data[available_cols]

            # Generate file
            filename = f"export_{export_type}_{created_at.strftime('%Y%m%d_%H%M%S')}"
            file_path = self._save_export(data, format, filename)

            # Record export metadata
            metadata = {
                "export_id": export_id,
                "created_at": created_at.isoformat(),
                "export_type": export_type,
                "format": format,
                "filename": f"{filename}.{format}",
                "file_path": str(file_path),
                "filters": filters or {},
                "columns": columns,
                "user_id": user_id,
                "nda_signed": nda_signed,
                "row_count": len(data) if isinstance(data, pd.DataFrame) else len(data),
                "status": "completed",
            }

            # Save metadata
            meta_path = self.exports_path / f"{filename}.meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(
                "export_completed",
                export_id=export_id,
                rows=metadata["row_count"],
            )

            return metadata

        except Exception as e:
            logger.error("export_failed", export_id=export_id, error=str(e))
            raise AppException(
                status_code=500,
                error_code="EXPORT_FAILED",
                message=f"Export failed: {str(e)}",
            )

    def _get_export_data(
        self,
        export_type: str,
        filters: Optional[Dict[str, Any]] = None,
        nda_signed: bool = False,
    ) -> pd.DataFrame:
        """Get data for export based on type."""
        if export_type == "audits_raw":
            audits = self.json_storage.list_audits(filters=filters, limit=100000)

            if not nda_signed:
                # Anonymize L0 data
                for audit in audits:
                    if "contact" in audit:
                        audit["contact"]["email"] = "REDACTED"
                        audit["contact"]["name"] = "REDACTED"
                        audit["contact"]["phone"] = "REDACTED"

            return self._audits_to_dataframe(audits)

        elif export_type == "audits_aggregated":
            try:
                return self.parquet_storage.load_master_dataset()
            except Exception:
                return pd.DataFrame()

        elif export_type == "benchmarks":
            benchmarks = self.parquet_storage.load_dataframe("benchmarks_all.parquet")
            return benchmarks

        elif export_type == "efa_dataset":
            return self._build_efa_dataset(filters)

        else:
            raise AppException(
                status_code=400,
                error_code="INVALID_EXPORT_TYPE",
                message=f"Unknown export type: {export_type}",
            )

    def _audits_to_dataframe(self, audits: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert audit list to flat DataFrame."""
        rows = []

        for audit in audits:
            row = {
                "audit_id": audit.get("audit_id"),
                "created_at": audit.get("created_at"),
                "status": audit.get("status"),
                "audit_type": audit.get("audit_type"),
                "industry": audit.get("company_profile", {}).get("industry"),
                "company_size": audit.get("company_profile", {}).get("company_size"),
                "region": audit.get("company_profile", {}).get("region"),
                "composite_score": audit.get("calculated_indices", {}).get(
                    "composite_score"
                ),
                "maturity_level": audit.get("calculated_indices", {}).get(
                    "maturity_level"
                ),
                "roi_estimate": audit.get("calculated_indices", {}).get(
                    "roi_estimate_percent"
                ),
                "tco_estimate": audit.get("calculated_indices", {}).get(
                    "tco_estimate_millions"
                ),
            }

            # Flatten dimension scores
            for dim_id, score in (
                audit.get("calculated_indices", {}).get("dimension_scores", {}).items()
            ):
                row[f"dim_{dim_id}_score"] = score

            # Flatten raw responses
            for resp in audit.get("raw_responses", []):
                col = f"d{resp['dimension_id']}_q{resp['question_id']}"
                row[col] = resp["score"]

            rows.append(row)

        return pd.DataFrame(rows)

    def _build_efa_dataset(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Build dataset suitable for Exploratory Factor Analysis."""
        audits = self.json_storage.list_audits(filters=filters, limit=100000)
        rows = []

        for audit in audits:
            if audit.get("status") == "archived":
                continue

            row = {"audit_id": audit.get("audit_id")}

            for resp in audit.get("raw_responses", []):
                col = f"D{resp['dimension_id']}_Q{resp['question_id']}"
                row[col] = resp["score"]

            rows.append(row)

        return pd.DataFrame(rows)

    def _save_export(self, data: pd.DataFrame, format: str, filename: str) -> Path:
        """Save export to file."""
        if format == "csv":
            file_path = self.exports_path / f"{filename}.csv"
            data.to_csv(file_path, index=False, encoding="utf-8-sig")
        elif format == "parquet":
            file_path = self.exports_path / f"{filename}.parquet"
            data.to_parquet(file_path, engine="pyarrow", index=False)
        elif format == "json":
            file_path = self.exports_path / f"{filename}.json"
            data.to_json(file_path, orient="records", force_ascii=False, indent=2)
        else:
            raise AppException(
                status_code=400,
                error_code="INVALID_FORMAT",
                message=f"Unsupported export format: {format}",
            )

        return file_path

    def get_export_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get history of exports."""
        history = []

        for meta_file in sorted(
            self.exports_path.glob("*.meta.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    history.append(json.load(f))
            except Exception:
                continue

            if len(history) >= limit:
                break

        return history

    def get_export_file_path(self, export_id: str) -> Optional[Path]:
        """Get file path for an export by ID."""
        for meta_file in self.exports_path.glob("*.meta.json"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    if meta.get("export_id") == export_id:
                        return Path(meta["file_path"])
            except Exception:
                continue

        return None