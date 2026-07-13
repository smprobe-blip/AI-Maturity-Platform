"""Radar chart calculation service.
v1.3 — Priority 2.1: benchmark loading from benchmarks.json.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from app.models.schemas import (
    CalculatedIndices,
    PatternInfo,
    BottleneckItem,
    AnchorItem,
    UpsellTrigger,
    GapAnalysis,
    DimensionGap,
)
from app.services.pattern_service import (
    detect_pattern,
    generate_upsell_triggers,
    get_top3_anchors,
    get_top3_bottlenecks,
    DIMENSIONS,
)


# ============================================================
# Constants
# ============================================================

DIMENSION_WEIGHTS = {
    '1': 0.15,
    '2': 0.15,
    '3': 0.15,
    '4': 0.15,
    '5': 0.15,
    '6': 0.20,
    '7': 0.05,
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

MATURITY_LEVELS = [
    (1.0, 1.8, 'Начальный', 'level-1'),
    (1.9, 2.6, 'AI-Enabled', 'level-2'),
    (2.7, 3.4, 'AI-Driven', 'level-3'),
    (3.5, 4.2, 'AI-First', 'level-4'),
    (4.3, 5.0, 'AI-Native', 'level-5'),
]

BENCHMARK_KEY_TO_DIM_ID = {
    'strategy': '1',
    'people': '2',
    'infrastructure': '3',
    'data': '4',
    'models': '5',
    'implementation': '6',
    'rnd': '7',
}

INDUSTRY_KEY_MAP = {
    'retail': 'Retail',
    'ecommerce': 'Retail',
    'finance': 'Finance',
    'fintech': 'Finance',
    'manufacturing': 'Manufacturing',
    'it': 'IT',
    'telecom': 'Services',
    'logistics': 'Services',
    'energy': 'Services',
    'healthcare': 'Healthcare',
    'education': 'Services',
    'government': 'Services',
    'other': 'CrossIndustry',
}


# ============================================================
# Benchmark loading
# ============================================================

def _find_benchmarks_file() -> Optional[Path]:
    """Find benchmarks.json in project tree."""
    current = Path(__file__).resolve().parent
    candidates = [
        current.parent.parent.parent / 'frontend' / 'data' / 'benchmarks.json',
        current.parent.parent / 'frontend' / 'data' / 'benchmarks.json',
        current.parent.parent / 'data' / 'benchmarks.json',
        current / 'data' / 'benchmarks.json',
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_benchmark(industry: str) -> Optional[Dict[str, float]]:
    """Load industry benchmark from benchmarks.json."""
    if not industry:
        return None
    
    file_path = _find_benchmarks_file()
    if not file_path:
        print(f'[benchmark] File not found, skipping for {industry}')
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        benchmarks = data.get('benchmarks', {})
        
        if industry in benchmarks:
            raw = benchmarks[industry]
        else:
            mapped_key = INDUSTRY_KEY_MAP.get(industry.lower(), 'CrossIndustry')
            raw = benchmarks.get(mapped_key, {})
            if not raw:
                for key in benchmarks:
                    if key.lower() == industry.lower():
                        raw = benchmarks[key]
                        break
        
        if not raw:
            print(f'[benchmark] No data for industry={industry}')
            return None
        
        result = {}
        for eng_key, score in raw.items():
            dim_id = BENCHMARK_KEY_TO_DIM_ID.get(eng_key.lower().strip())
            if dim_id:
                result[dim_id] = float(score)
        
        print(f'[benchmark] Loaded {len(result)} axes for {industry}')
        return result
        
    except Exception as e:
        print(f'[benchmark] Error loading for {industry}: {e}')
        return None


# ============================================================
# Core calculations
# ============================================================

def calculate_composite_score(dimension_scores: Dict[str, float]) -> float:
    """Calculate weighted composite score."""
    total = 0.0
    for dim_id, weight in DIMENSION_WEIGHTS.items():
        score = dimension_scores.get(dim_id, 0.0)
        total += score * weight
    return round(total, 2)


def determine_maturity_level(score: float) -> Tuple[str, str]:
    """Determine maturity level from composite score."""
    for low, high, level_name, level_code in MATURITY_LEVELS:
        if low <= score <= high:
            return level_name, level_code
    return 'AI-Native', 'level-5'


def estimate_roi(composite_score: float) -> float:
    """Estimate ROI improvement percent."""
    return round(max(0.0, (composite_score - 2.0) * 8.0), 1)


def estimate_tco(composite_score: float, company_size: str) -> float:
    """Estimate TCO in millions RUB."""
    base = {'small': 5, 'medium': 15, 'large': 40, 'enterprise': 120}
    multiplier = base.get(company_size, 15)
    return round((composite_score / 5.0) * multiplier, 1)


def _aggregate_dimension_scores(responses: Dict) -> Dict[str, float]:
    """Aggregate question-level responses to dimension scores."""
    dimension_scores = {}
    for dim_id in DIMENSION_WEIGHTS.keys():
        value = responses.get(dim_id)
        if value is None:
            dimension_scores[dim_id] = 0.0
            continue
        
        if isinstance(value, dict):
            scores = [float(v) for v in value.values() if v is not None]
            dimension_scores[dim_id] = sum(scores) / len(scores) if scores else 0.0
        else:
            dimension_scores[dim_id] = float(value)
        
        dimension_scores[dim_id] = max(1.0, min(5.0, dimension_scores[dim_id]))
    
    return dimension_scores


def calculate_gap_analysis(
    current_scores: Dict[str, float],
    target_scores: Optional[Dict[str, float]],
) -> Optional[GapAnalysis]:
    """Calculate gap analysis between current and target state."""
    if not target_scores:
        return None
    
    gaps: Dict[str, DimensionGap] = {}
    total_gap = 0.0
    
    for dim_id in DIMENSION_WEIGHTS.keys():
        current = current_scores.get(dim_id, 0.0)
        target = float(target_scores.get(dim_id, current))
        gap = target - current
        
        if gap > 1.5:
            priority = 'high'
        elif gap > 0.7:
            priority = 'medium'
        else:
            priority = 'low'
        
        gaps[dim_id] = DimensionGap(
            current=round(current, 2),
            target=round(target, 2),
            gap=round(gap, 2),
            priority=priority,
        )
        total_gap += abs(gap) * DIMENSION_WEIGHTS[dim_id]
    
    priority_axes = sorted(
        [gid for gid, g in gaps.items() if g.priority == 'high'],
        key=lambda x: gaps[x].gap,
        reverse=True,
    )
    
    return GapAnalysis(
        dimension_gaps=gaps,
        weighted_total_gap=round(total_gap, 2),
        priority_axes=priority_axes,
    )


def _get_field(item: Any, field: str, default: Any = None) -> Any:
    """Get field from dict or Pydantic model."""
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def generate_recommendations(
    dimension_scores: Dict[str, float],
    top3_bottlenecks: List[Any],
    top3_anchors: List[Any],
) -> List[str]:
    """Generate actionable recommendations."""
    recommendations = []
    
    for item in top3_bottlenecks:
        severity = _get_field(item, 'severity')
        dim_name = _get_field(item, 'dimension_name', '')
        score = _get_field(item, 'score', 0)
        
        if severity == 'critical':
            recommendations.append(
                f"Критическая зона: {dim_name} ({score:.1f}/5). Требуется срочное внимание и инвестиции."
            )
        elif severity == 'warning':
            recommendations.append(
                f"Зона роста: {dim_name} ({score:.1f}/5). Рекомендуется развитие компетенций."
            )
    
    for item in top3_anchors:
        strength = _get_field(item, 'strength')
        dim_name = _get_field(item, 'dimension_name', '')
        score = _get_field(item, 'score', 0)
        
        if strength == 'strong':
            recommendations.append(
                f"Опорная точка: {dim_name} ({score:.1f}/5). Использовать как якорь изменений."
            )
    
    return recommendations


# ============================================================
# Main entry point
# ============================================================

def calculate_indices(
    responses: Dict,
    company_size: str = 'medium',
    company_industry: Optional[str] = None,
    target_scores: Optional[Dict[str, float]] = None,
    benchmark_scores: Optional[Dict[str, float]] = None,
) -> Tuple[CalculatedIndices, List[Dict]]:
    """Calculate full set of indices from raw responses."""
    dimension_scores = _aggregate_dimension_scores(responses)
    composite = calculate_composite_score(dimension_scores)
    level_name, _level_code = determine_maturity_level(composite)
    roi = estimate_roi(composite)
    tco = estimate_tco(composite, company_size)
    
    # Load benchmark if not provided
    if benchmark_scores is None and company_industry:
        benchmark_scores = load_benchmark(company_industry)
    
    # Pattern detection
    pattern = detect_pattern(dimension_scores, benchmark_scores)
    
    # Top-3 analysis
    top3_bottlenecks = get_top3_bottlenecks(dimension_scores)
    top3_anchors = get_top3_anchors(dimension_scores)
    
    # Gap analysis
    gap_analysis = calculate_gap_analysis(dimension_scores, target_scores)
    
    # Upsell triggers
    upsell_triggers = generate_upsell_triggers(dimension_scores, pattern)
    
    # Build response WITH benchmark_scores
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
        benchmark_scores=benchmark_scores,  # NEW: include in response
    )
    
    return indices, upsell_triggers