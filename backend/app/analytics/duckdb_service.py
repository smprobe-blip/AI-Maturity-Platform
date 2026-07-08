"""DuckDB analytics service for advanced queries and statistical analysis."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb
import numpy as np
import pandas as pd
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class DuckDBAnalytics:
    """Advanced analytics using DuckDB SQL engine."""

    def __init__(self, raw_audits_path: Optional[str] = None):
        self.raw_audits_path = raw_audits_path or settings.raw_audits_path

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Create DuckDB connection."""
        return duckdb.connect(":memory:")

    def query_audits(self, sql: str) -> pd.DataFrame:
        """Execute arbitrary SQL query against audit JSON files."""
        conn = self._get_connection()

        try:
            # Register JSON files as a table
            json_pattern = f"{self.raw_audits_path}/**/*.json"

            query = sql.replace(
                "{audits_table}", f"read_json_auto('{json_pattern}')"
            )

            result = conn.execute(query).fetchdf()
            return result

        except Exception as e:
            logger.error("duckdb_query_failed", query=sql[:200], error=str(e))
            raise
        finally:
            conn.close()

    def calculate_benchmarks_sql(
        self, industry: Optional[str] = None
    ) -> pd.DataFrame:
        """Calculate benchmarks using DuckDB SQL."""
        conn = self._get_connection()

        try:
            json_pattern = f"{self.raw_audits_path}/**/*.json"

            where_clause = ""
            if industry:
                where_clause = f"WHERE company_profile->>'industry' = '{industry}'"

            query = f"""
                SELECT
                    company_profile->>'industry' as industry,
                    calculated_indices->>'composite_score' as composite_score,
                    calculated_indices->>'maturity_level' as maturity_level
                FROM read_json_auto('{json_pattern}')
                {where_clause}
            """

            df = conn.execute(query).fetchdf()

            # Convert score to numeric
            df["composite_score"] = pd.to_numeric(
                df["composite_score"], errors="coerce"
            )
            df = df.dropna(subset=["composite_score"])

            return df

        except Exception as e:
            logger.error("benchmark_sql_failed", error=str(e))
            return pd.DataFrame()
        finally:
            conn.close()

    def longitudinal_analysis(self) -> pd.DataFrame:
        """Analyze companies that have taken the assessment multiple times."""
        conn = self._get_connection()

        try:
            json_pattern = f"{self.raw_audits_path}/**/*.json"

            query = f"""
                SELECT
                    company_profile->>'industry' as industry,
                    company_profile->>'region' as region,
                    created_at,
                    calculated_indices->>'composite_score' as composite_score,
                    calculated_indices->>'maturity_level' as maturity_level
                FROM read_json_auto('{json_pattern}')
                WHERE status != 'archived'
                ORDER BY industry, created_at
            """

            return conn.execute(query).fetchdf()

        except Exception as e:
            logger.error("longitudinal_analysis_failed", error=str(e))
            return pd.DataFrame()
        finally:
            conn.close()

    def correlation_matrix(self) -> pd.DataFrame:
        """Compute correlation matrix between dimensions."""
        conn = self._get_connection()

        try:
            json_pattern = f"{self.raw_audits_path}/**/*.json"

            query = f"""
                SELECT
                    calculated_indices->'dimension_scores'->>'1' as dim1,
                    calculated_indices->'dimension_scores'->>'2' as dim2,
                    calculated_indices->'dimension_scores'->>'3' as dim3,
                    calculated_indices->'dimension_scores'->>'4' as dim4,
                    calculated_indices->'dimension_scores'->>'5' as dim5,
                    calculated_indices->'dimension_scores'->>'6' as dim6,
                    calculated_indices->'dimension_scores'->>'7' as dim7
                FROM read_json_auto('{json_pattern}')
                WHERE status != 'archived'
            """

            df = conn.execute(query).fetchdf()

            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            return df.corr()

        except Exception as e:
            logger.error("correlation_matrix_failed", error=str(e))
            return pd.DataFrame()
        finally:
            conn.close()

    def score_distribution(self) -> Dict[str, Any]:
        """Get score distribution statistics."""
        conn = self._get_connection()

        try:
            json_pattern = f"{self.raw_audits_path}/**/*.json"

            query = f"""
                SELECT
                    COUNT(*) as total,
                    AVG(CAST(calculated_indices->>'composite_score' AS DOUBLE)) as mean,
                    MIN(CAST(calculated_indices->>'composite_score' AS DOUBLE)) as min_val,
                    MAX(CAST(calculated_indices->>'composite_score' AS DOUBLE)) as max_val,
                    STDDEV(CAST(calculated_indices->>'composite_score' AS DOUBLE)) as std_dev
                FROM read_json_auto('{json_pattern}')
                WHERE status != 'archived'
            """

            result = conn.execute(query).fetchone()

            if not result or result[0] == 0:
                return {"total": 0, "message": "No data available"}

            return {
                "total": result[0],
                "mean": round(result[1], 2) if result[1] else 0,
                "min": round(result[2], 2) if result[2] else 0,
                "max": round(result[3], 2) if result[3] else 0,
                "std_dev": round(result[4], 2) if result[4] else 0,
            }

        except Exception as e:
            logger.error("score_distribution_failed", error=str(e))
            return {"error": str(e)}
        finally:
            conn.close()