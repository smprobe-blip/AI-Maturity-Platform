"""Tests for reliability analysis."""

import pytest
from app.analytics.reliability import ReliabilityService


class TestReliabilityService:
    @pytest.fixture
    def service(self, json_storage) -> ReliabilityService:
        svc = ReliabilityService()
        svc.storage = json_storage
        return svc

    def test_insufficient_data(self, service: ReliabilityService):
        result = service.cronbach_alpha(1)
        assert result["status"] == "insufficient_data"

    def test_interpret_alpha(self, service: ReliabilityService):
        assert service._interpret_alpha(0.95) == "excellent"
        assert service._interpret_alpha(0.85) == "good"
        assert service._interpret_alpha(0.75) == "acceptable"
        assert service._interpret_alpha(0.65) == "questionable"
        assert service._interpret_alpha(0.4) == "unacceptable"