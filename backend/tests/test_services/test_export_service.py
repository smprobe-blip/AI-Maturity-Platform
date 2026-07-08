"""Tests for ExportService."""

import pytest
from app.services.export_service import ExportService


class TestExportService:
    """Tests for ExportService."""

    @pytest.fixture
    def service(self) -> ExportService:
        return ExportService()

    def test_export_history_empty(self, service: ExportService):
        """Test empty export history."""
        history = service.get_export_history()
        assert isinstance(history, list)