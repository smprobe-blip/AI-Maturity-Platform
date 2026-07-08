"""Tests for factor analysis."""

import pytest
from app.analytics.factor_analysis import FactorAnalysisService


class TestFactorAnalysisService:
    @pytest.fixture
    def service(self, json_storage) -> FactorAnalysisService:
        svc = FactorAnalysisService()
        svc.storage = json_storage
        return svc

    def test_insufficient_data(self, service: FactorAnalysisService):
        result = service.run_efa()
        assert result["status"] == "insufficient_data"

    def test_interpret_kmo(self, service: FactorAnalysisService):
        assert service._interpret_kmo(0.95) == "marvelous"
        assert service._interpret_kmo(0.85) == "meritorious"
        assert service._interpret_kmo(0.75) == "middling"
        assert service._interpret_kmo(0.4) == "unacceptable"