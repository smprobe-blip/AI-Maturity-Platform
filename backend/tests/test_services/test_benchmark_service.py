"""Tests for BenchmarkService."""

import pytest
from app.services.benchmark_service import BenchmarkService


class TestBenchmarkService:
    """Tests for BenchmarkService."""

    @pytest.fixture
    def service(self, json_storage) -> BenchmarkService:
        svc = BenchmarkService()
        svc.json_storage = json_storage
        return svc

    def test_recalculate_empty(self, service: BenchmarkService):
        """Test recalculation with no data."""
        result = service.recalculate_all()
        assert result["status"] == "empty"

    def test_get_company_percentile_empty(self, service: BenchmarkService):
        """Test percentile with no data."""
        result = service.get_company_percentile(3.5)
        assert result["sample_size"] == 0