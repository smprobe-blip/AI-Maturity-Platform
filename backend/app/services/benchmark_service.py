"""Benchmark service — calculate and manage industry benchmarks."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import duckdb
import numpy as np
import pandas as pd
import structlog

from app.core.config import settings
from app.storage.json_storage import JSONStorage
from app.storage.parquet_storage import ParquetStorage

logger = structlog.get_logger()


class BenchmarkService:
    """Service for calculating and retrieving industry benchmarks."""

    def __init__(self):
        self.json_storage = JSONStorage()
        self.parquet_storage = ParquetStorage()

    def recalculate_all(self) -> Dict[str, Any]:
        """Recalculate all industry benchmarks."""
        logger.info("benchmark_recalculation_started")

        # Load all audits
        audits = self.json_storage.list_audits(limit=100000)

        if not audits:
            logger.warning("no_audits_for_benchmark")
            return {"status": "empty", "benchmarks": {}}

        # Convert to DataFrame
        rows = []
        for audit in audits:
            if audit.get("status") == "archived":
                continue

            indices = audit.get("calculated_indices", {})
            profile = audit.get("company_profile", {})

            row = {
                "audit_id": audit.get("audit_id"),
                "industry": profile.get("industry", "Unknown"),
                "company_size": profile.get("company_size", "Unknown"),
                "region": profile.get("region", "Unknown"),
                "composite_score": indices.get("composite_score", 0),
                "maturity_level": indices.get("maturity_level", ""),
            }

            # Add dimension scores
            for dim_id, score in indices.get("dimension_scores", {}).items():
                row[f"dim_{dim_id}_score"] = score

            rows.append(row)

        if not rows:
            return {"status": "empty", "benchmarks": {}}

        df = pd.DataFrame(rows)

        # Calculate benchmarks by industry
        benchmarks = {}
        for industry, group in df.groupby("industry"):
            benchmark = self._calculate_benchmark(group, industry)
            benchmarks[industry] = benchmark

            # Save to Parquet
            self.parquet_storage.save_benchmark(
                pd.DataFrame([benchmark]), industry=industry
            )

        # Save overall benchmark
        overall = self._calculate_benchmark(df, "all")
        benchmarks["all"] = overall

        # Save master dataset
        self.parquet_storage.save_dataframe(df, "master_dataset.parquet")

        logger.info(
            "benchmark_recalculation_completed",
            industries=len(benchmarks),
            total_audits=len(df),
        )

        return {
            "status": "completed",
            "total_audits": len(df),
            "industries": list(benchmarks.keys()),
            "benchmarks": benchmarks,
        }

    def _calculate_benchmark(self, df: pd.DataFrame, industry: str) -> Dict[str, Any]:
        """Calculate benchmark statistics for a group."""
        scores = df["composite_score"]

        benchmark = {
            "industry": industry,
            "sample_size": len(df),
            "mean_score": round(float(scores.mean()), 2),
            "median_score": round(float(scores.median()), 2),
            "std_dev": round(float(scores.std()), 2) if len(scores) > 1 else 0.0,
            "min_score": round(float(scores.min()), 2),
            "max_score": round(float(scores.max()), 2),
            "percentile_25": round(float(scores.quantile(0.25)), 2),
            "percentile_75": round(float(scores.quantile(0.75)), 2),
            "percentile_90": round(float(scores.quantile(0.90)), 2),
            "calculated_at": datetime.now().isoformat(),
        }

        # Dimension breakdowns
        dimension_breakdown = {}
        for col in df.columns:
            if col.startswith("dim_") and col.endswith("_score"):
                dim_id = col.replace("dim_", "").replace("_score", "")
                dim_scores = df[col].dropna()
                if len(dim_scores) > 0:
                    dimension_breakdown[dim_id] = {
                        "mean": round(float(dim_scores.mean()), 2),
                        "median": round(float(dim_scores.median()), 2),
                        "std_dev": (
                            round(float(dim_scores.std()), 2)
                            if len(dim_scores) > 1
                            else 0.0
                        ),
                    }

        benchmark["dimension_breakdown"] = dimension_breakdown

        return benchmark

    def get_benchmark(self, industry: str) -> Optional[Dict[str, Any]]:
        """Get benchmark for specific industry."""
        try:
            df = self.parquet_storage.load_dataframe(
                f"benchmarks_{industry.lower().replace(' ', '_')}.parquet"
            )
            if df.empty:
                return None
            return df.iloc[0].to_dict()
        except Exception:
            return None

    def get_all_benchmarks(self) -> List[Dict[str, Any]]:
        """Get all industry benchmarks."""
        benchmarks = []
        try:
            master = self.parquet_storage.load_master_dataset()
            if master.empty:
                return []

            for industry, group in master.groupby("industry"):
                benchmarks.append(self._calculate_benchmark(group, str(industry)))

        except Exception as e:
            logger.error("get_all_benchmarks_error", error=str(e))

        return benchmarks

    def get_company_percentile(
        self, composite_score: float, industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate where a company stands in the distribution."""
        try:
            master = self.parquet_storage.load_master_dataset()
            if master.empty:
                return {"percentile": 50, "sample_size": 0}

            if industry:
                subset = master[master["industry"] == industry]
            else:
                subset = master

            if len(subset) == 0:
                return {"percentile": 50, "sample_size": 0}

            scores = subset["composite_score"]
            percentile = float((scores <= composite_score).sum() / len(scores) * 100)

            return {
                "percentile": round(percentile, 1),
                "sample_size": len(subset),
                "industry": industry or "all",
                "mean": round(float(scores.mean()), 2),
            }

        except Exception as e:
            logger.error("percentile_calculation_error", error=str(e))
            return {"percentile": 50, "sample_size": 0, "error": str(e)}