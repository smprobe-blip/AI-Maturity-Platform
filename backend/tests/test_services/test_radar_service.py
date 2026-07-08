"""Tests for RadarService."""

import pytest

from app.models.audit import RawResponse
from app.services.radar_service import RadarService


class TestRadarService:
    """Tests for RadarService."""
    
    @pytest.fixture
    def radar_service(self) -> RadarService:
        """RadarService instance."""
        return RadarService()
    
    def test_calculate_indices_all_threes(
        self, radar_service: RadarService, sample_raw_responses: list
    ):
        """Test calculation with all scores = 3."""
        responses = [RawResponse(**r) for r in sample_raw_responses]
        indices = radar_service.calculate_indices(responses)
        
        # All dimensions should be 3.0
        for dim_id in range(1, 8):
            assert indices.dimension_scores[str(dim_id)] == 3.0
        
        # Composite should be 3.0 (weighted average of all 3s)
        assert indices.composite_score == 3.0
        assert indices.maturity_level == "L3 — Defined"
    
    def test_calculate_indices_all_ones(self, radar_service: RadarService):
        """Test calculation with all scores = 1 (minimum)."""
        responses = []
        for dim_id in range(1, 8):
            for q_id in range(1, 6):
                responses.append(
                    RawResponse(dimension_id=dim_id, question_id=q_id, score=1)
                )
        
        indices = radar_service.calculate_indices(responses)
        
        assert indices.composite_score == 1.0
        assert indices.maturity_level == "L1 — Initial"
        assert indices.roi_estimate_percent == 0.0
    
    def test_calculate_indices_all_fives(self, radar_service: RadarService):
        """Test calculation with all scores = 5 (maximum)."""
        responses = []
        for dim_id in range(1, 8):
            for q_id in range(1, 6):
                responses.append(
                    RawResponse(dimension_id=dim_id, question_id=q_id, score=5)
                )
        
        indices = radar_service.calculate_indices(responses)
        
        assert indices.composite_score == 5.0
        assert indices.maturity_level == "L5 — Optimizing"
        assert indices.roi_estimate_percent == 400.0
    
    def test_calculate_indices_mixed_scores(self, radar_service: RadarService):
        """Test calculation with mixed scores."""
        responses = []
        # Dimension 1: all 5s
        for q_id in range(1, 6):
            responses.append(RawResponse(dimension_id=1, question_id=q_id, score=5))
        # Dimensions 2-7: all 1s
        for dim_id in range(2, 8):
            for q_id in range(1, 6):
                responses.append(RawResponse(dimension_id=dim_id, question_id=q_id, score=1))
        
        indices = radar_service.calculate_indices(responses)
        
        # Dimension 1 should be 5.0, others 1.0
        assert indices.dimension_scores["1"] == 5.0
        for dim_id in range(2, 8):
            assert indices.dimension_scores[str(dim_id)] == 1.0
        
        # Composite: 5.0 * 0.15 + 1.0 * 0.85 = 0.75 + 0.85 = 1.6
        assert abs(indices.composite_score - 1.6) < 0.01
    
    def test_get_radar_chart_data(self, radar_service: RadarService):
        """Test radar chart data preparation."""
        dimension_scores = {"1": 3.5, "2": 4.0, "3": 2.8}
        chart_data = radar_service.get_radar_chart_data(dimension_scores)
        
        assert len(chart_data) == 3
        assert chart_data[0]["dimension"] == "Strategy & Vision"
        assert chart_data[0]["score"] == 3.5
        assert chart_data[0]["max_score"] == 5.0
    
    def test_maturity_levels(self, radar_service: RadarService):
        """Test maturity level determination."""
        assert radar_service._get_maturity_level(1.0) == "L1 — Initial"
        assert radar_service._get_maturity_level(2.0) == "L2 — Developing"
        assert radar_service._get_maturity_level(3.0) == "L3 — Defined"
        assert radar_service._get_maturity_level(4.0) == "L4 — Managed"
        assert radar_service._get_maturity_level(4.8) == "L5 — Optimizing"