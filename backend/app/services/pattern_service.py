"""Dynamic pattern detection for radar chart diagnosis.
Implements 5 patterns from Concept v5.0 Table 3.3.
"""
from typing import Dict, List, Optional
from app.models.schemas import PatternInfo


DIMENSIONS = {
    '1': {'name': 'Стратегия и управление', 'weight': 0.15, 'group': 'governance'},
    '2': {'name': 'Люди и культура', 'weight': 0.15, 'group': 'people'},
    '3': {'name': 'Инфраструктура', 'weight': 0.15, 'group': 'tech'},
    '4': {'name': 'Данные', 'weight': 0.15, 'group': 'tech'},
    '5': {'name': 'Модели', 'weight': 0.15, 'group': 'tech'},
    '6': {'name': 'Внедрение ИИ', 'weight': 0.20, 'group': 'execution'},
    '7': {'name': 'Исследования (R&D)', 'weight': 0.05, 'group': 'rd'},
}


def _avg(scores: List[float]) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def detect_pattern(
    dimension_scores: Dict[str, float],
    benchmark_scores: Optional[Dict[str, float]] = None,
) -> PatternInfo:
    """Detect radar pattern and return diagnosis."""
    scores = [dimension_scores.get(str(i), 0.0) for i in range(1, 8)]
    avg = _avg(scores)

    if all(s <= 2.0 for s in scores):
        return PatternInfo(
            pattern_type='compressed_circle',
            diagnosis='Системная незрелость',
            recommendation=(
                'Начать со Стратегии и Инфраструктуры. '
                'Все оси на начальном уровне — требуется комплексная программа трансформации.'
            ),
            severity='critical',
        )

    tech_avg = _avg([scores[2], scores[3], scores[4]])
    people_score = scores[1]
    if tech_avg - people_score > 1.2:
        return PatternInfo(
            pattern_type='right_skew',
            diagnosis='Технократический перекос',
            recommendation=(
                'Инвестиции в ИИ-академию и культуру. '
                'Технологии опережают людей — пилоты заглохнут без change management.'
            ),
            severity='warning',
        )

    strategy_score = scores[0]
    implementation_score = scores[5]
    if strategy_score - implementation_score > 1.2:
        return PatternInfo(
            pattern_type='left_skew',
            diagnosis='Стратегия без исполнения',
            recommendation=(
                'Запуск AgentOps-пилотов и MLOps. '
                'Есть видение, но нет операционного контура внедрения.'
            ),
            severity='warning',
        )

    weak_axes = [str(i + 1) for i, s in enumerate(scores) if s <= 2.0]
    if 1 <= len(weak_axes) <= 2 and avg >= 3.0:
        weak_names = [DIMENSIONS[wid]['name'] for wid in weak_axes]
        return PatternInfo(
            pattern_type='star_with_gaps',
            diagnosis='Точечные узкие горлышка',
            recommendation=(
                f'Адресные инвестиции в проблемные оси: {", ".join(weak_names)}. '
                f'Остальные оси — опорные точки для масштабирования.'
            ),
            severity='warning',
        )

    if benchmark_scores:
        bench_scores = [benchmark_scores.get(str(i), 0.0) for i in range(1, 8)]
        deviations = [abs(s - b) for s, b in zip(scores, bench_scores)]
        avg_deviation = _avg(deviations)
        if avg_deviation < 0.4 and avg >= 2.5:
            return PatternInfo(
                pattern_type='benchmark_parity',
                diagnosis='Отраслевой паритет',
                recommendation=(
                    'Риск отсутствия дифференциации. '
                    'Инвестировать в R&D и уникальные компетенции для создания конкурентного преимущества.'
                ),
                severity='info',
            )

    return PatternInfo(
        pattern_type='balanced',
        diagnosis='Сбалансированное развитие',
        recommendation=(
            'Продолжать текущую стратегию. '
            'Фокус на усилении сильных сторон и постепенной работе над зонами роста.'
        ),
        severity='success',
    )


def get_top3_bottlenecks(dimension_scores: Dict[str, float]) -> List[Dict]:
    """Get top-3 weakest dimensions (bottlenecks)."""
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
    result = []
    for dim_id, score in sorted_dims[:3]:
        dim_info = DIMENSIONS.get(dim_id, {'name': f'Ось {dim_id}', 'weight': 0.15})
        if score < 2.0:
            severity = 'critical'
        elif score < 2.7:
            severity = 'warning'
        else:
            severity = 'info'
        result.append({
            'dimension_id': dim_id,
            'dimension_name': dim_info['name'],
            'score': round(score, 2),
            'severity': severity,
            'weight': dim_info.get('weight', 0.15),
        })
    return result


def get_top3_anchors(dimension_scores: Dict[str, float]) -> List[Dict]:
    """Get top-3 strongest dimensions (anchors for change)."""
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for dim_id, score in sorted_dims[:3]:
        dim_info = DIMENSIONS.get(dim_id, {'name': f'Ось {dim_id}', 'weight': 0.15})
        if score >= 4.0:
            strength = 'strong'
        elif score >= 3.0:
            strength = 'moderate'
        else:
            strength = 'weak'
        result.append({
            'dimension_id': dim_id,
            'dimension_name': dim_info['name'],
            'score': round(score, 2),
            'strength': strength,
            'weight': dim_info.get('weight', 0.15),
        })
    return result


def generate_upsell_triggers(
    dimension_scores: Dict[str, float],
    pattern: PatternInfo,
) -> List[Dict]:
    """Generate upsell triggers based on dimension scores and pattern."""
    triggers = []

    if dimension_scores.get('3', 5.0) < 2.5:
        triggers.append({
            'type': 'fear_of_loss',
            'dimension_id': '3',
            'dimension_name': 'Инфраструктура (вкл. AI Governance)',
            'score': dimension_scores.get('3', 0),
            'risk': 'При масштабировании создаёт риск утечки данных и штрафов',
            'service': 'Аудит AI Governance и внедрение политик безопасности',
            'price_hint': '600 000 ₽',
        })

    if dimension_scores.get('4', 5.0) < 2.5:
        triggers.append({
            'type': 'bottleneck',
            'dimension_id': '4',
            'dimension_name': 'Данные',
            'score': dimension_scores.get('4', 0),
            'risk': 'Блокирует любые инвестиции в модели. Невозможно масштабировать ИИ без Фабрики данных',
            'service': 'Проектирование и развёртывание Фабрики данных (Data Lakehouse)',
            'price_hint': 'от 1.5 млн ₽',
        })

    if dimension_scores.get('2', 5.0) < 2.5:
        triggers.append({
            'type': 'new_roles',
            'dimension_id': '2',
            'dimension_name': 'Люди и культура',
            'score': dimension_scores.get('2', 0),
            'risk': 'Нет выделенных операторов ИИ-систем и AI Automation Engineer. Пилоты заглохнут',
            'service': 'Аутстафф ИИ-команды или Корпоративная ИИ-Академия',
            'price_hint': 'от 800 000 ₽',
        })

    if dimension_scores.get('6', 5.0) < 2.5:
        triggers.append({
            'type': 'methodology',
            'dimension_id': '6',
            'dimension_name': 'Внедрение ИИ',
            'score': dimension_scores.get('6', 0),
            'risk': 'Отсутствие единого фреймворка приведёт к "пилотному болоту"',
            'service': 'Внедрение фреймворка AgentOps (сквозной контур создания и мониторинга ИИ-агентов)',
            'price_hint': 'от 2.0 млн ₽',
        })

    return triggers