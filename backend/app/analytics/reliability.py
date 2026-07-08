"""Reliability analysis — Cronbach's alpha, McDonald's omega, split-half."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import pingouin as pg
import structlog
from scipy import stats

from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class ReliabilityService:
    """Service for reliability analysis of measurement scales."""

    def __init__(self):
        self.storage = JSONStorage()

    def _get_dimension_data(self, dimension_id: int) -> pd.DataFrame:
        """Get raw responses for a specific dimension."""
        audits = self.storage.list_audits(limit=100000)
        active = [a for a in audits if a.get("status") != "archived"]

        rows = []
        for audit in active:
            row = {"audit_id": audit.get("audit_id")}
            for resp in audit.get("raw_responses", []):
                if resp["dimension_id"] == dimension_id:
                    row[f"Q{resp['question_id']}"] = resp["score"]
            if len(row) == 6:  # audit_id + 5 questions
                rows.append(row)

        df = pd.DataFrame(rows).set_index("audit_id")
        return df

    def cronbach_alpha(self, dimension_id: int) -> Dict[str, Any]:
        """Calculate Cronbach's alpha for a dimension."""
        df = self._get_dimension_data(dimension_id)

        if len(df) < 10:
            return {
                "status": "insufficient_data",
                "dimension_id": dimension_id,
                "sample_size": len(df),
            }

        # Cronbach's alpha using pingouin
        alpha_result = pg.cronbach_alpha(df)
        alpha, ci = alpha_result

        # Item-total statistics
        item_stats = self._item_total_statistics(df)

        # Alpha if item deleted
        alpha_if_deleted = {}
        for col in df.columns:
            remaining = df.drop(columns=[col])
            if remaining.shape[1] >= 2:
                a, _ = pg.cronbach_alpha(remaining)
                alpha_if_deleted[col] = float(a)

        return {
            "status": "completed",
            "dimension_id": dimension_id,
            "sample_size": len(df),
            "n_items": df.shape[1],
            "alpha": float(alpha),
            "ci_95": [float(ci[0]), float(ci[1])],
            "interpretation": self._interpret_alpha(alpha),
            "item_statistics": item_stats,
            "alpha_if_deleted": alpha_if_deleted,
        }

    def _item_total_statistics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate item-total statistics."""
        total = df.sum(axis=1)
        stats_list = []

        for col in df.columns:
            item = df[col]
            rest = total - item

            # Correlation with total
            corr, p = stats.pearsonr(item, rest)

            # Squared multiple correlation
            from sklearn.linear_model import LinearRegression

            X = df.drop(columns=[col]).values
            y = item.values
            lr = LinearRegression().fit(X, y)
            smc = lr.score(X, y)

            stats_list.append(
                {
                    "item": col,
                    "mean": float(item.mean()),
                    "std": float(item.std()),
                    "item_rest_correlation": float(corr),
                    "p_value": float(p),
                    "squared_multiple_correlation": float(smc),
                }
            )

        return stats_list

    def _interpret_alpha(self, alpha: float) -> str:
        """Interpret Cronbach's alpha value."""
        if alpha >= 0.9:
            return "excellent"
        elif alpha >= 0.8:
            return "good"
        elif alpha >= 0.7:
            return "acceptable"
        elif alpha >= 0.6:
            return "questionable"
        elif alpha >= 0.5:
            return "poor"
        else:
            return "unacceptable"

    def mcdonalds_omega(self, dimension_id: int) -> Dict[str, Any]:
        """Calculate McDonald's omega (hierarchical reliability)."""
        df = self._get_dimension_data(dimension_id)

        if len(df) < 30:
            return {"status": "insufficient_data", "sample_size": len(df)}

        try:
            # Simplified omega calculation
            corr_matrix = df.corr().values
            eigenvalues = np.linalg.eigvalsh(corr_matrix)[::-1]

            # Omega total
            loadings = np.sqrt(np.maximum(eigenvalues[0], 0))
            omega = (loadings**2) / (
                loadings**2 + np.sum(np.maximum(eigenvalues[1:], 0))
            )

            return {
                "status": "completed",
                "dimension_id": dimension_id,
                "sample_size": len(df),
                "omega_total": float(omega),
                "interpretation": self._interpret_alpha(omega),
            }

        except Exception as e:
            logger.error("omega_calculation_failed", error=str(e))
            return {"status": "error", "error": str(e)}

    def split_half_reliability(self, dimension_id: int) -> Dict[str, Any]:
        """Calculate split-half reliability."""
        df = self._get_dimension_data(dimension_id)

        if len(df) < 10 or df.shape[1] < 4:
            return {"status": "insufficient_data"}

        # Split items into two halves
        items = df.columns.tolist()
        half1 = items[: len(items) // 2]
        half2 = items[len(items) // 2 :]

        score1 = df[half1].sum(axis=1)
        score2 = df[half2].sum(axis=1)

        # Spearman-Brown corrected correlation
        corr, p = stats.pearsonr(score1, score2)
        sb_corrected = (2 * corr) / (1 + corr)

        return {
            "status": "completed",
            "dimension_id": dimension_id,
            "sample_size": len(df),
            "split_half_correlation": float(corr),
            "spearman_brown_corrected": float(sb_corrected),
            "p_value": float(p),
        }

    def composite_reliability(self, dimension_id: int) -> Dict[str, Any]:
        """Calculate composite reliability (CR)."""
        df = self._get_dimension_data(dimension_id)

        if len(df) < 30:
            return {"status": "insufficient_data"}

        # Get factor loadings from EFA
        from app.analytics.factor_analysis import FactorAnalysisService

        fa_service = FactorAnalysisService()
        efa_result = fa_service.run_efa(n_factors=7)

        if efa_result.get("status") != "completed":
            return {"status": "error", "message": "EFA not available"}

        # Extract loadings for this dimension
        loadings = []
        for i in range(1, 6):
            item = f"D{dimension_id:02d}_Q{i:02d}"
            if item in efa_result["loadings"]:
                # Get max loading across factors
                max_loading = max(
                    abs(v) for v in efa_result["loadings"][item].values()
                )
                loadings.append(max_loading)

        if not loadings:
            return {"status": "error", "message": "No loadings found"}

        # CR formula
        sum_loadings = sum(loadings)
        sum_error = sum(1 - l**2 for l in loadings)
        cr = (sum_loadings**2) / (sum_loadings**2 + sum_error)

        return {
            "status": "completed",
            "dimension_id": dimension_id,
            "composite_reliability": float(cr),
            "interpretation": self._interpret_alpha(cr),
        }

    def average_variance_extracted(self, dimension_id: int) -> Dict[str, Any]:
        """Calculate Average Variance Extracted (AVE)."""
        df = self._get_dimension_data(dimension_id)

        if len(df) < 30:
            return {"status": "insufficient_data"}

        from app.analytics.factor_analysis import FactorAnalysisService

        fa_service = FactorAnalysisService()
        efa_result = fa_service.run_efa(n_factors=7)

        if efa_result.get("status") != "completed":
            return {"status": "error"}

        loadings = []
        for i in range(1, 6):
            item = f"D{dimension_id:02d}_Q{i:02d}"
            if item in efa_result["loadings"]:
                max_loading = max(
                    abs(v) for v in efa_result["loadings"][item].values()
                )
                loadings.append(max_loading)

        if not loadings:
            return {"status": "error"}

        # AVE formula
        ave = sum(l**2 for l in loadings) / len(loadings)

        return {
            "status": "completed",
            "dimension_id": dimension_id,
            "average_variance_extracted": float(ave),
            "interpretation": "adequate" if ave >= 0.5 else "inadequate",
        }

    def full_reliability_report(self) -> Dict[str, Any]:
        """Generate comprehensive reliability report for all dimensions."""
        report = {"dimensions": {}, "summary": {}}

        for dim_id in range(1, 8):
            alpha_result = self.cronbach_alpha(dim_id)
            omega_result = self.mcdonalds_omega(dim_id)
            split_result = self.split_half_reliability(dim_id)
            cr_result = self.composite_reliability(dim_id)
            ave_result = self.average_variance_extracted(dim_id)

            report["dimensions"][str(dim_id)] = {
                "cronbach_alpha": alpha_result,
                "mcdonalds_omega": omega_result,
                "split_half": split_result,
                "composite_reliability": cr_result,
                "average_variance_extracted": ave_result,
            }

        # Summary
        alphas = [
            report["dimensions"][str(d)]["cronbach_alpha"].get("alpha", 0)
            for d in range(1, 8)
            if report["dimensions"][str(d)]["cronbach_alpha"].get("status") == "completed"
        ]

        report["summary"] = {
            "mean_alpha": float(np.mean(alphas)) if alphas else 0,
            "min_alpha": float(np.min(alphas)) if alphas else 0,
            "max_alpha": float(np.max(alphas)) if alphas else 0,
            "all_acceptable": all(a >= 0.7 for a in alphas),
        }

        return report