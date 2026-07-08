"""Parquet storage for aggregated data and analytics."""

from pathlib import Path
from typing import Optional

import pandas as pd
import structlog

from app.core.config import settings
from app.core.exceptions import StorageException

logger = structlog.get_logger()


class ParquetStorage:
    """Storage for Parquet files (aggregated data)."""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.aggregated_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_dataframe(self, df: pd.DataFrame, filename: str) -> str:
        """Save DataFrame to Parquet file."""
        file_path = self.base_path / filename
        
        try:
            df.to_parquet(file_path, engine="pyarrow", compression="snappy", index=False)
            logger.info("parquet_saved", path=str(file_path), rows=len(df))
            return str(file_path)
        
        except Exception as e:
            logger.error("parquet_save_failed", path=str(file_path), error=str(e))
            raise StorageException("save_dataframe", {"filename": filename, "error": str(e)})
    
    def load_dataframe(self, filename: str) -> pd.DataFrame:
        """Load DataFrame from Parquet file."""
        file_path = self.base_path / filename
        
        if not file_path.exists():
            raise StorageException("load_dataframe", {"filename": filename, "error": "File not found"})
        
        try:
            df = pd.read_parquet(file_path, engine="pyarrow")
            logger.info("parquet_loaded", path=str(file_path), rows=len(df))
            return df
        
        except Exception as e:
            logger.error("parquet_load_failed", path=str(file_path), error=str(e))
            raise StorageException("load_dataframe", {"filename": filename, "error": str(e)})
    
    def load_master_dataset(self) -> pd.DataFrame:
        """Load master dataset (all audits in Parquet format)."""
        master_file = self.base_path / "master_dataset.parquet"
        
        if not master_file.exists():
            # Return empty DataFrame if not exists
            return pd.DataFrame()
        
        return self.load_dataframe("master_dataset.parquet")
    
    def save_benchmark(self, benchmark_df: pd.DataFrame, industry: Optional[str] = None) -> str:
        """Save benchmark data."""
        if industry:
            filename = f"benchmarks_{industry.lower().replace(' ', '_')}.parquet"
        else:
            filename = "benchmarks_all.parquet"
        
        return self.save_dataframe(benchmark_df, filename)