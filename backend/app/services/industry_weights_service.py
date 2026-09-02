"""Динамические отраслевые веса осей ИИ-зрелости (алгоритм А.1-А.2 диссертации).

w_d(g) = lambda_g * w_emp_d(g) + (1 - lambda_g) * w0_d,   lambda_g = n_g / (n_g + k),  k = 30
w_emp_d(g) = max(beta_d; eps) / sum_j max(beta_j; eps),   eps = 0.05

Ограничения: w_d в [0.05; 0.25], нормировка sum(w) = 1.
При n_g < k эмпирическая поправка не применяется (возврат к базовому/экспертному профилю).
"""
from typing import Dict, Optional, Tuple

K = 30
W_MIN, W_MAX = 0.05, 0.25
EPS = 0.05

# Базовые веса методики (гл. 2.10 диссертации)
BASE_WEIGHTS: Dict[str, float] = {
    '1': 0.15, '2': 0.15, '3': 0.15, '4': 0.15, '5': 0.15, '6': 0.20, '7': 0.05,
}

# Экспертные отраслевые профили (п. 2.11.2): для регулируемых отраслей вес
# управления/данных повышен компенсаторным снижением R&D; для производства
# усилены инфраструктура и модели.
EXPERT_PROFILES: Dict[str, Dict[str, float]] = {
    'finance': {'1': 0.20, '2': 0.10, '3': 0.15, '4': 0.20, '5': 0.15, '6': 0.15, '7': 0.05},
    'fintech': {'1': 0.20, '2': 0.10, '3': 0.15, '4': 0.20, '5': 0.15, '6': 0.15, '7': 0.05},
    'government': {'1': 0.20, '2': 0.10, '3': 0.15, '4': 0.20, '5': 0.10, '6': 0.20, '7': 0.05},
    'manufacturing': {'1': 0.10, '2': 0.10, '3': 0.20, '4': 0.15, '5': 0.20, '6': 0.15, '7': 0.10},
}


def _clamp_normalize(weights: Dict[str, float]) -> Dict[str, float]:
    """Итеративный клампинг в [W_MIN; W_MAX] с перенормировкой (водозаполнение)."""
    w = {d: max(W_MIN, float(v)) for d, v in weights.items()}
    for _ in range(10):
        over = {d: v for d, v in w.items() if v > W_MAX}
        if not over:
            break
        excess = sum(v - W_MAX for v in over.values())
        for d in over:
            w[d] = W_MAX
        room = {d: v for d, v in w.items() if d not in over and v < W_MAX}
        room_total = sum(room.values()) or 1.0
        for d, v in room.items():
            w[d] = v + excess * (v / room_total)
    w = {d: round(v, 4) for d, v in w.items()}
    drift = round(1.0 - sum(w.values()), 4)
    if abs(drift) >= 0.0001:
        w[drift > 0 and max(w, key=w.get) or min(w, key=w.get)] += drift
    return w


def compute_industry_weights(
    industry: Optional[str] = None,
    n_g: int = 0,
    beta: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Веса осей для отрасли g по формулам А.1-А.2."""
    ind = (industry or '').lower().strip()
    base = dict(EXPERT_PROFILES.get(ind, BASE_WEIGHTS))
    if not beta or (n_g or 0) < K:
        return _clamp_normalize(base)
    floored = {d: max(EPS, float(beta.get(d, 0.0))) for d in base}
    total = sum(floored.values())
    w_emp = {d: v / total for d, v in floored.items()}          # А.2
    lam = n_g / (n_g + K)                                        # А.1
    mixed = {d: lam * w_emp[d] + (1 - lam) * base[d] for d in base}
    return _clamp_normalize(mixed)


def get_industry_weights(
    industry: Optional[str] = None,
    n_g: int = 0,
    beta: Optional[Dict[str, float]] = None,
) -> Tuple[Dict[str, float], str]:
    """Точка входа: возвращает (веса, источник). Источники: base / expert_profile / empirical."""
    ind = (industry or '').lower().strip()
    if not beta or (n_g or 0) < K:
        source = 'expert_profile' if ind in EXPERT_PROFILES else 'base'
        return compute_industry_weights(ind, 0, None), source
    return compute_industry_weights(ind, n_g, beta), 'empirical'
