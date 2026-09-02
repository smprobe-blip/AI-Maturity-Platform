"""Тесты алгоритма динамических отраслевых весов (А.1-А.2)."""
import pytest
from app.services.industry_weights_service import (
    BASE_WEIGHTS,
    compute_industry_weights,
    get_industry_weights,
)
from app.services.radar_service import calculate_composite_score


def test_unknown_industry_returns_base():
    w, src = get_industry_weights('unknown_industry')
    assert w == BASE_WEIGHTS
    assert src == 'base'


def test_expert_profile_applied():
    w, src = get_industry_weights('finance')
    assert src == 'expert_profile'
    assert w['1'] > BASE_WEIGHTS['1']   # регулируемая отрасль: управление тяжелее
    assert w['2'] < BASE_WEIGHTS['2']


def test_weights_clamped_and_normalized():
    w = compute_industry_weights('retail', n_g=60, beta={'2': 0.9, '5': 0.1})
    assert all(0.05 - 1e-9 <= v <= 0.25 + 1e-9 for v in w.values())
    assert abs(sum(w.values()) - 1.0) < 1e-6
    assert w['2'] == 0.25               # продвинутая ось упирается в потолок


def test_small_sample_falls_back():
    beta = {'2': 0.9, '5': 0.1}
    w_small, _ = get_industry_weights('retail', n_g=10, beta=beta)
    assert w_small == BASE_WEIGHTS      # n_g < 30: эмпирика не применяется


def test_shrinkage_pulls_toward_base():
    beta = {'2': 0.9, '5': 0.1}
    w = compute_industry_weights('retail', n_g=300, beta=beta)
    assert w['2'] > BASE_WEIGHTS['2']   # эмпирика подняла ось 2
    assert 0.15 <= w['2'] <= 0.25


def test_composite_uses_custom_weights():
    dims = {'1': 5.0, '2': 1.0, '3': 3.0, '4': 3.0, '5': 3.0, '6': 3.0, '7': 3.0}
    base = calculate_composite_score(dims)
    custom = calculate_composite_score(dims, weights={'1': 0.25, '2': 0.15, '3': 0.15,
                                                      '4': 0.15, '5': 0.15, '6': 0.10, '7': 0.05})
    assert custom > base                # ось 1 с максимальным баллом получила больший вес
