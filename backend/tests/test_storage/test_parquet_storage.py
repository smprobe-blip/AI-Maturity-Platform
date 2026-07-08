"""Tests for Parquet storage."""

import pandas as pd
import pytest

from app.storage.parquet_storage import ParquetStorage


class TestParquetStorage:
    """Tests for ParquetStorage."""
    
    def test_save_and_load_dataframe(self, parquet_storage: ParquetStorage):
        """Test saving and loading DataFrame."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [3.5, 4.0, 2.8],
        })
        
        # Save
        path = parquet_storage.save_dataframe(df, "test_data.parquet")
        assert path.endswith("test_data.parquet")
        
        # Load
        loaded = parquet_storage.load_dataframe("test_data.parquet")
        assert len(loaded) == 3
        assert list(loaded.columns) == ["id", "name", "score"]
    
    def test_load_nonexistent_file(self, parquet_storage: ParquetStorage):
        """Test loading non-existent file raises error."""
        from app.core.exceptions import StorageException
        
        with pytest.raises(StorageException):
            parquet_storage.load_dataframe("nonexistent.parquet")
    
    def test_save_benchmark(self, parquet_storage: ParquetStorage):
        """Test saving benchmark data."""
        df = pd.DataFrame({
            "industry": ["Retail", "Finance"],
            "avg_score": [3.2, 3.8],
        })
        
        path = parquet_storage.save_benchmark(df, industry="Retail")
        assert "benchmarks_retail" in path