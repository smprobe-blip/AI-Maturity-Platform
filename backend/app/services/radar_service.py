"""Radar chart service — calculate maturity indices."""

from typing import Dict, List

from app.models.audit import CalculatedIndices, RawResponse

# Dimension weights (sum = 100%)
DIMENSION_WEIGHTS = {
    1: 0.15,  # Strategy
    2: 0.15,  # Data
    3: 0.15,  # Technology
    4: 0.15,  # Processes
    5: 0.15,  # People
    6: 0.20,  # Culture
    7: 0.05,  # Ethics
}

# Maturity levels
MATURITY_LEVELS = {
    (0, 1.5): "L1 — Initial",
    (1.5, 2.5): "L2 — Developing",
    (2.5, 3.5): "L3 — Defined",
    (3.5, 4.5): "L4 — Managed",
    (4.5, 5.0): "L5 — Optimizing",
}


class RadarService:
    """Service for calculating maturity indices and radar chart data."""
    
    def calculate_indices(self, raw_responses: List[RawResponse]) -> CalculatedIndices:
        """Calculate maturity indices from raw responses."""
        # Group responses by dimension
        dimension_scores: Dict[int, List[int]] = {}
        
        for response in raw_responses:
            dim_id = response.dimension_id
            if dim_id not in dimension_scores:
                dimension_scores[dim_id] = []
            dimension_scores[dim_id].append(response.score)
        
        # Calculate average score per dimension
        dimension_averages = {}
        for dim_id, scores in dimension_scores.items():
            dimension_averages[str(dim_id)] = sum(scores) / len(scores)
        
        # Calculate composite score (weighted average)
        composite_score = sum(
            dimension_averages[str(dim_id)] * weight
            for dim_id, weight in DIMENSION_WEIGHTS.items()
        )
        
        # Determine maturity level
        maturity_level = self._get_maturity_level(composite_score)
        
        # Estimate ROI (simplified formula)
        roi_estimate = self._estimate_roi(composite_score)
        
        # Estimate TCO (simplified formula)
        tco_estimate = self._estimate_tco(composite_score)
        
        return CalculatedIndices(
            dimension_scores=dimension_averages,
            composite_score=round(composite_score, 2),
            maturity_level=maturity_level,
            roi_estimate_percent=round(roi_estimate, 1),
            tco_estimate_millions=round(tco_estimate, 2),
        )
    
    def _get_maturity_level(self, score: float) -> str:
        """Determine maturity level from composite score."""
        for (min_score, max_score), level in MATURITY_LEVELS.items():
            if min_score <= score < max_score:
                return level
        return "L5 — Optimizing"
    
    def _estimate_roi(self, maturity_score: float) -> float:
        """Estimate ROI based on maturity score (simplified)."""
        # Simplified formula: ROI increases with maturity
        # L1 (1.0) → 0%, L3 (3.0) → 150%, L5 (5.0) → 400%
        return max(0, (maturity_score - 1.0) * 100)
    
    def _estimate_tco(self, maturity_score: float) -> float:
        """Estimate TCO in millions based on maturity score (simplified)."""
        # Simplified formula: TCO increases with maturity
        # L1 (1.0) → 5M, L3 (3.0) → 25M, L5 (5.0) → 80M
        return max(5.0, maturity_score * 15.0)
    
    def get_radar_chart_data(self, dimension_scores: Dict[str, float]) -> List[Dict[str, any]]:
        """Prepare data for radar chart visualization."""
        dimension_names = {
            "1": "Strategy & Vision",
            "2": "Data & Analytics",
            "3": "Technology & Infrastructure",
            "4": "Processes & Operations",
            "5": "People & Skills",
            "6": "Culture & Change",
            "7": "Ethics & Governance",
        }
        
        return [
            {
                "dimension": dimension_names.get(str(dim_id), f"Dimension {dim_id}"),
                "score": round(score, 2),
                "max_score": 5.0,
            }
            for dim_id, score in dimension_scores.items()
        ]