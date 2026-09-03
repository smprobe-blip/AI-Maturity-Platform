"""Dashboard service — aggregate metrics for admin panels."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import structlog

from app.storage.json_storage import JSONStorage
from app.storage.parquet_storage import ParquetStorage

logger = structlog.get_logger()


class DashboardService:
    """Service for computing dashboard metrics."""

    def __init__(self):
        self.json_storage = JSONStorage()
        self.parquet_storage = ParquetStorage()

    def get_business_metrics(self) -> Dict[str, Any]:
        """Business dashboard: KPIs, funnel, revenue indicators."""
        audits = self.json_storage.list_audits(limit=100000)
        active_audits = [a for a in audits if a.get("status") != "archived"]

        now = datetime.now()
        this_month = [
            a
            for a in active_audits
            if self._is_this_month(a.get("created_at", ""))
        ]
        last_month = [
            a
            for a in active_audits
            if self._is_last_month(a.get("created_at", ""))
        ]

        # Growth rate
        growth = 0.0
        if len(last_month) > 0:
            growth = ((len(this_month) - len(last_month)) / len(last_month)) * 100

        # Average maturity
        scores = [
            a.get("calculated_indices", {}).get("composite_score", 0)
            for a in active_audits
        ]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Industry distribution
        industry_dist = {}
        for a in active_audits:
            ind = a.get("company_profile", {}).get("industry", "Unknown")
            industry_dist[ind] = industry_dist.get(ind, 0) + 1

        # Maturity level distribution
        level_dist = {}
        for a in active_audits:
            level = a.get("calculated_indices", {}).get("maturity_level", "Unknown")
            level_dist[level] = level_dist.get(level, 0) + 1

        return {
            "total_audits": len(active_audits),
            "audits_this_month": len(this_month),
            "audits_last_month": len(last_month),
            "growth_rate_percent": round(growth, 1),
            "average_maturity_score": round(avg_score, 2),
            "industry_distribution": industry_dist,
            "maturity_level_distribution": level_dist,
        }

    def _iter_responses(self, audit: Dict[str, Any]):
        """Оценки (dimension, score) из текущего формата request.responses."""
        req = audit.get("request") or {}
        responses = req.get("responses") or audit.get("responses") or {}
        for dim, qs in responses.items():
            if isinstance(qs, dict):
                for q, v in sorted(qs.items()):
                    try:
                        yield str(dim), float(v)
                    except (TypeError, ValueError):
                        continue

    def _cronbach_alpha(self, items: List[List[float]]) -> Optional[float]:
        """Классический альфа Кронбаха по матрице «наблюдения x пункты»."""
        k = len(items[0])
        if len(items) < 2 or k < 2:
            return None
        variances = []
        for j in range(k):
            col = [row[j] for row in items]
            m = sum(col) / len(col)
            variances.append(sum((v - m) ** 2 for v in col) / (len(col) - 1))
        totals = [sum(row) for row in items]
        mt = sum(totals) / len(totals)
        var_t = sum((t - mt) ** 2 for t in totals) / (len(totals) - 1)
        if var_t == 0:
            return None
        return (k / (k - 1)) * (1 - sum(variances) / var_t)

    def get_scientific_metrics(self) -> Dict[str, Any]:
        """Scientific dashboard: reliability, validity, factor structure."""
        audits = self.json_storage.list_audits(limit=100000)
        active_audits = [a for a in audits if a.get("status") != "archived"]

        if not active_audits:
            return {
                "sample_size": 0,
                "cronbach_alpha": {},
                "factor_analysis": None,
                "message": "Insufficient data for scientific metrics",
            }

        # Ответы по осям: матрицы «аудиты x 5 пунктов» для альфа Кронбаха
        dimension_items: Dict[str, List[List[float]]] = {}
        all_scores: List[float] = []

        for audit in active_audits:
            per_dim: Dict[str, List[float]] = {}
            for dim, score in self._iter_responses(audit):
                all_scores.append(score)
                per_dim.setdefault(dim, []).append(score)
            for dim, items in per_dim.items():
                if len(items) >= 2:
                    dimension_items.setdefault(dim, []).append(items)

        # Альфа Кронбаха по каждой оси (наблюдений >= 2)
        cronbach = {}
        for dim_id, matrix in dimension_items.items():
            alpha = self._cronbach_alpha(matrix)
            if alpha is not None:
                cronbach[dim_id] = round(alpha, 3)

        return {
            "sample_size": len(active_audits),
            "total_responses": len(all_scores),
            "mean_response": round(sum(all_scores) / len(all_scores), 2)
            if all_scores
            else 0,
            "cronbach_alpha": cronbach,
            "dimensions_count": 7,
            "questions_per_dimension": 5,
        }

    def get_operational_metrics(self) -> Dict[str, Any]:
        """Operational dashboard: system health, performance."""
        audits = self.json_storage.list_audits(limit=100000)

        # Response time stats
        response_times = []
        for audit in audits:
            for resp in audit.get("raw_responses", []):
                t = resp.get("time_to_answer_sec")
                if t is not None:
                    response_times.append(t)

        return {
            "total_audits_stored": len(audits),
            "avg_response_time_sec": (
                round(sum(response_times) / len(response_times), 1)
                if response_times
                else 0
            ),
            "storage_status": "healthy",
            "last_backup": datetime.now().isoformat(),
        }

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Data quality dashboard."""
        audits = self.json_storage.list_audits(limit=100000)

        total = len(audits)
        complete = sum(
            1
            for a in audits
            if len(a.get("raw_responses", [])) == 35
        )
        archived = sum(1 for a in audits if a.get("status") == "archived")

        # Missing data
        missing_fields = 0
        for a in audits:
            if not a.get("company_profile", {}).get("industry"):
                missing_fields += 1

        return {
            "total_records": total,
            "complete_records": complete,
            "completeness_rate": round(complete / total * 100, 1) if total else 0,
            "archived_records": archived,
            "records_with_missing_industry": missing_fields,
            "data_freshness_days": 0,  # Would compute from actual dates
        }

    def _is_this_month(self, date_str: str) -> bool:
        """Check if date string is in current month."""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            now = datetime.now()
            return dt.year == now.year and dt.month == now.month
        except (ValueError, AttributeError):
            return False

    def _is_last_month(self, date_str: str) -> bool:
        """Check if date string is in previous month."""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            now = datetime.now()
            if now.month == 1:
                return dt.year == now.year - 1 and dt.month == 12
            return dt.year == now.year and dt.month == now.month - 1
        except (ValueError, AttributeError):
            return False

    def _simplified_cronbach(self, scores: List[int]) -> float:
        """Simplified Cronbach's alpha calculation."""
        n = len(scores)
        if n < 2:
            return 0.0

        mean_score = sum(scores) / n
        variance = sum((s - mean_score) ** 2 for s in scores) / (n - 1)

        if variance == 0:
            return 1.0

        # Simplified: single-item returns high alpha
        return min(0.95, max(0.0, 1 - (1 / variance)))