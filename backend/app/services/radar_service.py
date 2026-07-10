"""Radar chart calculation service.
v1.1 — Priority 1: 35 questions, patterns, top-3, gap analysis, upsell.
"""
from typing import Dict, List, Optional, Tuple, Any
from app.models.schemas import CalculatedIndices, PatternInfo
from app.services.pattern_service import (
    detect_pattern,
    generate_upsell_triggers,
    get_top3_anchors,
    get_top3_bottlenecks,
    DIMENSIONS,
)


# Weights per dimension (sum = 1.0) — Concept v6.0 Table 4.2.1
DIMENSION_WEIGHTS = {
    '1': 0.15,  # Strategy & Governance
    '2': 0.15,  # People & Culture
    '3': 0.15,  # Infrastructure
    '4': 0.15,  # Data
    '5': 0.15,  # Models
    '6': 0.20,  # AI Implementation (accent)
    '7': 0.05,  # R&D
}

DIMENSION_NAMES = {
    '1': 'Стратегия и управление',
    '2': 'Люди и культура',
    '3': 'Инфраструктура',
    '4': 'Данные',
    '5': 'Модели',
    '6': 'Внедрение ИИ',
    '7': 'Исследования (R&D)',
}

# Concept v5.0 Table 3.2: Maturity zones
MATURITY_LEVELS = [
    (1.0, 1.8, 'Начальный', 'level-1'),
    (1.9, 2.6, 'AI-Enabled', 'level-2'),
    (2.7, 3.4, 'AI-Driven', 'level-3'),
    (3.5, 4.2, 'AI-First', 'level-4'),
    (4.3, 5.0, 'AI-Native', 'level-5'),
]


def calculate_composite_score(dimension_scores: Dict[str, float]) -> float:
    """Calculate weighted composite score."""
    total = 0.0
    for dim_id, weight in DIMENSION_WEIGHTS.items():
        score = dimension_scores.get(dim_id, 0.0)
        total += score * weight
    return round(total, 2)


def determine_maturity_level(score: float) -> Tuple[str, str]:
    """Determine maturity level from composite score.
    
    Returns:
        Tuple of (level_name, level_code)
    """
    for low, high, level_name, level_code in MATURITY_LEVELS:
        if low <= score <= high:
            return level_name, level_code
    return 'AI-Native', 'level-5'


def estimate_roi(composite_score: float) -> float:
    """Estimate ROI improvement percent based on maturity.
    
    Simple linear model: each point above 2.0 gives ~8% ROI.
    """
    return round(max(0.0, (composite_score - 2.0) * 8.0), 1)


def estimate_tco(composite_score: float, company_size: str) -> float:
    """Estimate TCO in millions RUB."""
    base = {'small': 5, 'medium': 15, 'large': 40, 'enterprise': 120}
    multiplier = base.get(company_size, 15)
    return round((composite_score / 5.0) * multiplier, 1)


def _aggregate_dimension_scores(responses: Dict) -> Dict[str, float]:
    """Aggregate question-level responses to dimension scores.
    
    Supports two formats (backward compatible):
    1. Flat: {'1': 3.5, '2': 2.0, ...} — single score per axis
    2. Nested: {'1': {'1': 4, '2': 3, ...}, ...} — 35 questions (Priority 1)
    """
    dimension_scores = {}
    for dim_id in DIMENSION_WEIGHTS.keys():
        value = responses.get(dim_id)
        if value is None:
            dimension_scores[dim_id] = 0.0
            continue
        
        if isinstance(value, dict):
            # Nested format: average of 5 questions
            scores = [float(v) for v in value.values() if v is not None]
            dimension_scores[dim_id] = sum(scores) / len(scores) if scores else 0.0
        else:
            # Flat format: direct score
            dimension_scores[dim_id] = float(value)
        
        # Clamp to 1-5
        dimension_scores[dim_id] = max(1.0, min(5.0, dimension_scores[dim_id]))
    
    return dimension_scores


def calculate_gap_analysis(
    current_scores: Dict[str, float],
    target_scores: Optional[Dict[str, float]],
) -> Optional[Dict]:
    """Calculate gap analysis between current and target state."""
    if not target_scores:
        return None
    
    gaps = {}
    total_gap = 0.0
    for dim_id in DIMENSION_WEIGHTS.keys():
        current = current_scores.get(dim_id, 0.0)
        target = float(target_scores.get(dim_id, current))
        gap = target - current
        gaps[dim_id] = {
            'current': round(current, 2),
            'target': round(target, 2),
            'gap': round(gap, 2),
            'priority': 'high' if gap > 1.5 else ('medium' if gap > 0.7 else 'low'),
        }
        total_gap += abs(gap) * DIMENSION_WEIGHTS[dim_id]
    
    return {
        'dimension_gaps': gaps,
        'weighted_total_gap': round(total_gap, 2),
        'priority_axes': sorted(
            [gid for gid, g in gaps.items() if g['priority'] == 'high'],
            key=lambda x: gaps[x]['gap'],
            reverse=True,
        ),
    }


def _get_field(item: Any, field: str, default: Any = None) -> Any:
    """Get field from dict or Pydantic model (support both formats)."""
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def generate_recommendations(
    dimension_scores: Dict[str, float],
    top3_bottlenecks: List[Any],
    top3_anchors: List[Any],
) -> List[str]:
    """Generate actionable recommendations based on analysis.
    
    Supports both dict and Pydantic model items (backward compatible).
    """
    recommendations = []
    
    # Top-3 bottlenecks
    for item in top3_bottlenecks:
        severity = _get_field(item, 'severity')
        dim_name = _get_field(item, 'dimension_name', '')
        score = _get_field(item, 'score', 0)
        
        if severity == 'critical':
            recommendations.append(
                f"🚨 Критическая зона: {dim_name} ({score:.1f}/5). "
                f"Требуется срочное внимание и инвестиции."
            )
        elif severity == 'warning':
            recommendations.append(
                f"⚠️ Зона роста: {dim_name} ({score:.1f}/5). "
                f"Рекомендуется развитие компетенций."
            )
    
    # Top-3 anchors
    for item in top3_anchors:
        strength = _get_field(item, 'strength')
        dim_name = _get_field(item, 'dimension_name', '')
        score = _get_field(item, 'score', 0)
        
        if strength == 'strong':
            recommendations.append(
                f"💪 Опорная точка: {dim_name} ({score:.1f}/5). "
                f"Использовать как якорь изменений."
            )
    
    return recommendations


def calculate_indices(
    responses: Dict,
    company_size: str = 'medium',
    target_scores: Optional[Dict[str, float]] = None,
    benchmark_scores: Optional[Dict[str, float]] = None,
) -> Tuple[CalculatedIndices, List[Dict]]:
    """Calculate full set of indices from raw responses.
    
    Args:
        responses: Dimension responses (flat or nested format)
        company_size: Company size category
        target_scores: Optional target scores for gap analysis
        benchmark_scores: Optional industry benchmark for pattern detection
    
    Returns:
        Tuple of (CalculatedIndices, upsell_triggers)
    """
    dimension_scores = _aggregate_dimension_scores(responses)
    composite = calculate_composite_score(dimension_scores)
    level_name, _level_code = determine_maturity_level(composite)
    roi = estimate_roi(composite)
    tco = estimate_tco(composite, company_size)
    
    # Pattern detection (Priority 1)
    pattern = detect_pattern(dimension_scores, benchmark_scores)
    
    # Top-3 analysis (Priority 1)
    top3_bottlenecks = get_top3_bottlenecks(dimension_scores)
    top3_anchors = get_top3_anchors(dimension_scores)
    
    # Gap analysis (Priority 1)
    gap_analysis = calculate_gap_analysis(dimension_scores, target_scores)
    
    # Upsell triggers (Priority 1)
    upsell_triggers = generate_upsell_triggers(dimension_scores, pattern)
    
    indices = CalculatedIndices(
        composite_score=composite,
        maturity_level=level_name,
        dimension_scores=dimension_scores,
        roi_estimate_percent=roi,
        tco_estimate_millions=tco,
        top3_bottlenecks=top3_bottlenecks,
        top3_anchors=top3_anchors,
        pattern=pattern,
        gap_analysis=gap_analysis,
    )
    
    return indices, upsell_triggers