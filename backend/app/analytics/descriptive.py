"""Descriptive statistics for the dataset."""

from typing import Any, Dict, List

import numpy as np
import pandas as pd
import structlog
from scipy import stats

from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class DescriptiveStatisticsService:
    """Service for descriptive statistics."""

    def __init__(self):
        self.storage = JSONStorage()

    def _prepare_dataset(self) -> pd.DataFrame:
        """Prepare dataset."""
        audits = self.storage.list_audits(limit=100000)
        active = [a for a in audits if a.get("status") != "archived"]

        rows = []
        for audit in active:
            indices = audit.get("calculated_indices", {})
            profile = audit.get("company_profile", {})

            row = {
                "audit_id": audit.get("audit_id"),
                "created_at": audit.get("created_at"),
                "industry": profile.get("industry", ""),
                "company_size": profile.get("company_size", ""),
                "region": profile.get("region", ""),
                "ai_experience_years": profile.get("ai_experience_years", 0),
                "it_budget_millions": profile.get("annual_it_budget_millions", 0),
                "composite_score": indices.get("composite_score", 0),
                "maturity_level": indices.get("maturity_level", ""),
                "roi_percent": indices.get("roi_estimate_percent", 0),
                "tco_millions": indices.get("tco_estimate_millions", 0),
            }

            for dim_id, score in indices.get("dimension_scores", {}).items():
                row[f"dim_{dim_id}"] = score

            rows.append(row)

        return pd.DataFrame(rows)

    def sample_characteristics(self) -> Dict[str, Any]:
        """Sample characteristics for dissertation."""
        df = self._prepare_dataset()

        return {
            "total_sample_size": len(df),
            "date_range": {
                "first": df["created_at"].min() if not df.empty else None,
                "last": df["created_at"].max() if not df.empty else None,
            },
            "industry_distribution": df["industry"].value_counts().to_dict(),
            "size_distribution": df["company_size"].value_counts().to_dict(),
            "region_distribution": df["region"].value_counts().to_dict(),
            "maturity_level_distribution": df["maturity_level"].value_counts().to_dict(),
        }

    def central_tendency(self) -> Dict[str, Any]:
        """Measures of central tendency."""
        df = self._prepare_dataset()

        if df.empty:
            return {"status": "no_data"}

        results = {}

        # Composite score
        composite = df["composite_score"]
        results["composite_score"] = {
            "mean": float(composite.mean()),
            "median": float(composite.median()),
            "mode": float(composite.mode()[0]) if not composite.mode().empty else None,
            "std": float(composite.std()),
            "variance": float(composite.var()),
            "skewness": float(composite.skew()),
            "kurtosis": float(composite.kurtosis()),
        }

        # Dimension scores
        for i in range(1, 8):
            col = f"dim_{i}"
            if col in df.columns:
                dim = df[col]
                results[col] = {
                    "mean": float(dim.mean()),
                    "median": float(dim.median()),
                    "std": float(dim.std()),
                    "min": float(dim.min()),
                    "max": float(dim.max()),
                    "q1": float(dim.quantile(0.25)),
                    "q3": float(dim.quantile(0.75)),
                    "iqr": float(dim.quantile(0.75) - dim.quantile(0.25)),
                }

        return results

    def distribution_analysis(self) -> Dict[str, Any]:
        """Distribution analysis with normality tests."""
        df = self._prepare_dataset()

        if df.empty:
            return {"status": "no_data"}

        results = {}

        # Composite score
        composite = df["composite_score"]

        # Normality tests
        shapiro_stat, shapiro_p = stats.shapiro(composite[:500])
        ks_stat, ks_p = stats.kstest(composite, "norm", args=(composite.mean(), composite.std()))

        # Histogram data
        hist, bin_edges = np.histogram(composite, bins=20)

        results["composite_score"] = {
            "normality_tests": {
                "shapiro_wilk": {"statistic": float(shapiro_stat), "p_value": float(shapiro_p)},
                "kolmogorov_smirnov": {"statistic": float(ks_stat), "p_value": float(ks_p)},
                "is_normal": shapiro_p > 0.05,
            },
            "histogram": {
                "counts": hist.tolist(),
                "bin_edges": bin_edges.tolist(),
            },
            "percentiles": {
                "p5": float(composite.quantile(0.05)),
                "p10": float(composite.quantile(0.10)),
                "p25": float(composite.quantile(0.25)),
                "p50": float(composite.quantile(0.50)),
                "p75": float(composite.quantile(0.75)),
                "p90": float(composite.quantile(0.90)),
                "p95": float(composite.quantile(0.95)),
            },
        }

        return results

    def correlation_analysis(self) -> Dict[str, Any]:
        """Correlation matrix between dimensions."""
        df = self._prepare_dataset()

        if df.empty:
            return {"status": "no_data"}

        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        corr_matrix = df[dim_cols].corr()

        # Significance tests
        p_values = pd.DataFrame(index=dim_cols, columns=dim_cols)
        for i in dim_cols:
            for j in dim_cols:
                if i == j:
                    p_values.loc[i, j] = 0.0
                else:
                    _, p = stats.pearsonr(df[i], df[j])
                    p_values.loc[i, j] = p

        return {
            "correlation_matrix": corr_matrix.round(3).to_dict(),
            "p_values": p_values.astype(float).round(4).to_dict(),
            "significant_correlations": self._count_significant(corr_matrix, p_values),
        }

    def _count_significant(self, corr: pd.DataFrame, p_vals: pd.DataFrame) -> int:
        """Count significant correlations."""
        count = 0
        for i in corr.columns:
            for j in corr.columns:
                if i < j and p_vals.loc[i, j] < 0.05:
                    count += 1
        return count

    def outliers_analysis(self) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        df = self._prepare_dataset()

        if df.empty:
            return {"status": "no_data"}

        composite = df["composite_score"]

        # IQR method
        q1 = composite.quantile(0.25)
        q3 = composite.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = composite[(composite < lower_bound) | (composite > upper_bound)]

        # Z-score method
        z_scores = np.abs(stats.zscore(composite))
        z_outliers = composite[z_scores > 3]

        # Mahalanobis distance (multivariate)
        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        try:
            from scipy.spatial.distance import mahalanobis

            data = df[dim_cols].values
            mean = np.mean(data, axis=0)
            cov = np.cov(data, rowvar=False)
            cov_inv = np.linalg.inv(cov)

            mahal_distances = np.array(
                [mahalanobis(mean, row, cov_inv) for row in data]
            )
            threshold = np.sqrt(len(dim_cols) * 3)  # Chi-square threshold
            mahal_outliers = np.sum(mahal_distances > threshold)
        except Exception:
            mahal_outliers = 0

        return {
            "iqr_method": {
                "count": len(iqr_outliers),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            },
            "zscore_method": {
                "count": len(z_outliers),
                "threshold": 3.0,
            },
            "mahalanobis_method": {
                "count": int(mahal_outliers),
            },
            "recommendation": "Remove outliers before parametric tests"
            if len(iqr_outliers) > len(df) * 0.05
            else "Outlier count acceptable",
        }

    def full_descriptive_report(self) -> Dict[str, Any]:
        """Generate complete descriptive statistics report."""
        return {
            "sample_characteristics": self.sample_characteristics(),
            "central_tendency": self.central_tendency(),
            "distribution_analysis": self.distribution_analysis(),
            "correlation_analysis": self.correlation_analysis(),
            "outliers_analysis": self.outliers_analysis(),
        }