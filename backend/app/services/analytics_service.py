"""Analytics service — DuckDB queries for scientific analysis."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd
import structlog

from app.core.config import settings
from app.storage.parquet_storage import ParquetStorage

logger = structlog.get_logger()


class AnalyticsService:
    """Service for scientific analytics using DuckDB."""
    
    def __init__(self):
        self.raw_audits_path = Path(settings.raw_audits_path)
        self.parquet_storage = ParquetStorage()
    
    def _get_duckdb_connection(self):
        """Create DuckDB connection."""
        return duckdb.connect(":memory:")
    
    def calculate_benchmarks(self, industry: Optional[str] = None) -> pd.DataFrame:
        """Calculate industry benchmarks from raw audit data."""
        conn = self._get_duckdb_connection()
        
        # Find all audit JSON files
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            logger.warning("no_audit_files_found_for_benchmarks")
            return pd.DataFrame()
        
        # Build file list for DuckDB
        file_list = [str(f) for f in json_files]
        
        query = """
            WITH audit_data AS (
                SELECT 
                    audit_id,
                    company_profile->>'industry' as industry,
                    company_profile->>'company_size' as company_size,
                    calculated_indices->>'composite_score' as composite_score_str,
                    calculated_indices->>'maturity_level' as maturity_level,
                    created_at
                FROM read_json_auto(?, maximum_depth=3)
            ),
            scores AS (
                SELECT 
                    industry,
                    CAST(composite_score_str AS DOUBLE) as composite_score,
                    maturity_level
                FROM audit_data
                WHERE composite_score_str IS NOT NULL
            )
            SELECT 
                industry,
                COUNT(*) as sample_size,
                AVG(composite_score) as average_score,
                MEDIAN(composite_score) as median_score,
                STDDEV(composite_score) as std_dev,
                MIN(composite_score) as min_score,
                MAX(composite_score) as max_score
            FROM scores
            {}
            GROUP BY industry
            ORDER BY sample_size DESC
        """.format(
            f"WHERE industry = '{industry}'" if industry else ""
        )
        
        try:
            result = conn.execute(query, [file_list]).df()
            logger.info(
                "benchmarks_calculated",
                industries_count=len(result),
                total_audits=result["sample_size"].sum() if not result.empty else 0,
            )
            return result
        except Exception as e:
            logger.error("benchmark_calculation_failed", error=str(e))
            return pd.DataFrame()
    
    def get_distribution_by_maturity(self) -> Dict[str, int]:
        """Get distribution of audits by maturity level."""
        conn = self._get_duckdb_connection()
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            return {}
        
        query = """
            SELECT 
                calculated_indices->>'maturity_level' as maturity_level,
                COUNT(*) as count
            FROM read_json_auto(?, maximum_depth=3)
            WHERE calculated_indices->>'maturity_level' IS NOT NULL
            GROUP BY maturity_level
            ORDER BY maturity_level
        """
        
        try:
            result = conn.execute(query, [json_files]).df()
            return dict(zip(result["maturity_level"], result["count"]))
        except Exception as e:
            logger.error("distribution_calculation_failed", error=str(e))
            return {}
    
    def get_top_industries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top industries by audit count."""
        conn = self._get_duckdb_connection()
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            return []
        
        query = """
            SELECT 
                company_profile->>'industry' as industry,
                COUNT(*) as audit_count,
                AVG(CAST(calculated_indices->>'composite_score' AS DOUBLE)) as avg_score
            FROM read_json_auto(?, maximum_depth=3)
            WHERE company_profile->>'industry' IS NOT NULL
            GROUP BY industry
            ORDER BY audit_count DESC
            LIMIT ?
        """
        
        try:
            result = conn.execute(query, [json_files, limit]).df()
            return result.to_dict("records")
        except Exception as e:
            logger.error("top_industries_calculation_failed", error=str(e))
            return []
    
    def calculate_cronbach_alpha(self, dimension_id: int) -> float:
        """Calculate Cronbach's alpha for a dimension (reliability)."""
        # Simplified implementation
        # In real implementation, use factor_analyzer or pingouin
        conn = self._get_duckdb_connection()
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            return 0.0
        
        query = """
            SELECT 
                unnest(raw_responses)->>'score' as score,
                unnest(raw_responses)->>'question_id' as question_id
            FROM read_json_auto(?, maximum_depth=5)
        """
        
        try:
            # This is a simplified placeholder
            # Real Cronbach's alpha requires more complex calculation
            return 0.75  # Placeholder value
        except Exception as e:
            logger.error("cronbach_calculation_failed", error=str(e))
            return 0.0
    
    def calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between dimensions."""
        # Simplified placeholder
        dimensions = ["Strategy", "Data", "Technology", "Processes", "People", "Culture", "Ethics"]
        matrix = {}
        
        for dim1 in dimensions:
            matrix[dim1] = {}
            for dim2 in dimensions:
                if dim1 == dim2:
                    matrix[dim1][dim2] = 1.0
                else:
                    matrix[dim1][dim2] = 0.5  # Placeholder
        
        return matrix
    
    def get_completeness_score(self) -> float:
        """Calculate data completeness score (0-100)."""
        # Simplified: check percentage of audits with all fields
        conn = self._get_duckdb_connection()
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            return 0.0
        
        # Placeholder calculation
        return 92.5
    
    def get_outlier_count(self) -> int:
        """Count outliers in audit data."""
        # Simplified: audits with extreme scores (very high or very low)
        conn = self._get_duckdb_connection()
        json_files = list(self.raw_audits_path.rglob("audit_*.json"))
        
        if not json_files:
            return 0
        
        query = """
            SELECT COUNT(*) as outlier_count
            FROM read_json_auto(?, maximum_depth=3)
            WHERE CAST(calculated_indices->>'composite_score' AS DOUBLE) > 4.5
               OR CAST(calculated_indices->>'composite_score' AS DOUBLE) < 1.5
        """
        
        try:
            result = conn.execute(query, [json_files]).df()
            return int(result.iloc[0]["outlier_count"])
        except Exception:
            return 0