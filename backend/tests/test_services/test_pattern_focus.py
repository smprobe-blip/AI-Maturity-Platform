"""Паттерн определяет порядок рекомендаций и апселл-триггеров (утверждение с лендинга)."""
import pytest
from app.models.schemas import PatternInfo
from app.services.pattern_service import (
    detect_pattern,
    get_pattern_focus_axes,
    get_top3_bottlenecks,
    get_top3_anchors,
    generate_upsell_triggers,
)
from app.services.radar_service import generate_recommendations


def _mk(vals):
    return {str(i): v for i, v in enumerate(vals, start=1)}


PARITY_BENCH = _mk([3.1, 2.8, 2.9, 2.9, 2.9, 2.9, 3.1])


def test_static_focus_axes():
    p = PatternInfo(pattern_type='left_skew', diagnosis='x', recommendation='y', severity='warning')
    assert get_pattern_focus_axes(p, _mk([3.5, 3.0, 3.0, 2.2, 2.4, 1.8, 2.2])) == ['6']
    assert get_pattern_focus_axes(None, _mk([3.0] * 7)) == []


def test_single_anchor_focus_is_top_axis():
    dims = _mk([1.6, 4.4, 1.8, 1.6, 1.6, 1.2, 1.4])
    p = detect_pattern(dims, _mk([3.0, 2.4, 2.8, 2.6, 2.2, 2.5, 1.4]))
    assert p.pattern_type in ('people_anchor', 'single_anchor')
    assert '2' in get_pattern_focus_axes(p, dims)


def test_benchmark_parity_detected():
    dims = _mk([3.0, 2.7, 2.8, 2.5, 2.7, 2.5, 2.6])
    p = detect_pattern(dims, PARITY_BENCH)
    assert p.pattern_type == 'benchmark_parity'
    assert get_pattern_focus_axes(p, dims) == ['7']


def test_recommendations_parity_rnd_first():
    """При отраслевом паритете R&D (ось 7) выходит в начало рекомендаций."""
    dims = _mk([3.0, 2.7, 2.8, 2.5, 2.7, 2.5, 2.6])
    p = detect_pattern(dims, PARITY_BENCH)
    recs = generate_recommendations(
        dims,
        get_top3_bottlenecks(dims),
        get_top3_anchors(dims),
        pattern=p,
    )
    assert len(recs) >= 3
    assert 'R&D' in recs[0], recs
    recs_plain = generate_recommendations(
        dims,
        get_top3_bottlenecks(dims),
        get_top3_anchors(dims),
    )
    assert 'R&D' in recs_plain[-1]


def test_recommendations_anchor_first_for_people_anchor():
    dims = _mk([1.6, 4.4, 1.8, 1.6, 1.6, 1.2, 1.4])
    p = detect_pattern(dims, _mk([3.0, 2.4, 2.8, 2.6, 2.2, 2.5, 1.4]))
    assert p.pattern_type == 'people_anchor'
    recs = generate_recommendations(
        dims,
        get_top3_bottlenecks(dims),
        get_top3_anchors(dims),
        pattern=p,
    )
    assert recs[0].startswith('Опорная точка: Люди и культура')


def test_upsell_triggers_promoted_by_pattern():
    """При отраслевом паритете R&D поднимается в топ-3 триггеров."""
    dims = _mk([3.0, 2.7, 2.8, 2.5, 2.7, 2.5, 2.6])
    p = detect_pattern(dims, PARITY_BENCH)
    triggers = generate_upsell_triggers(dims, p)
    ids = [t['dimension_id'] for t in triggers]
    assert '7' in ids
    assert ids[0] == '7'
