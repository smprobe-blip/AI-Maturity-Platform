"""Tests for DashboardService."""

import pytest
from app.services.dashboard_service import DashboardService


class TestDashboardService:
    """Tests for DashboardService."""

    @pytest.fixture
    def service(self, json_storage) -> DashboardService:
        svc = DashboardService()
        svc.json_storage = json_storage
        return svc

    def test_business_metrics_empty(self, service: DashboardService):
        """Test business metrics with no data."""
        metrics = service.get_business_metrics()
        assert metrics["total_audits"] == 0
        assert metrics["average_maturity_score"] == 0.0

    def test_scientific_metrics_empty(self, service: DashboardService):
        """Test scientific metrics with no data."""
        metrics = service.get_scientific_metrics()
        assert metrics["sample_size"] == 0

    def test_quality_metrics_empty(self, service: DashboardService):
        """Test quality metrics with no data."""
        metrics = service.get_quality_metrics()
        assert metrics["total_records"] == 0