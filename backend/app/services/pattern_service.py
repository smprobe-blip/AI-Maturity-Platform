"""Dynamic pattern detection for radar chart diagnosis.
Implements 5 patterns from Concept v5.0 Table 3.3.
"""
from typing import Dict, List, Optional
from app.models.schemas import PatternInfo

DIM_NAMES = {'1': 'Стратегия', '2': 'Люди', '3': 'Инфраструктура', '4': 'Данные', '5': 'Модели', '6': 'Внедрение', '7': 'R&D'}

UPSELL_TEMPLATES = {
    '1': {'service': 'Воркшоп по AI-стратегии', 'price_hint': 'от 120 000 ₽', 'duration': '1 неделя', 'deliverables': ['Roadmap на 12 мес', 'Оценка бюджета'], 'case_study': 'Retail клиент: ROI 250% за год.'},
    '2': {'service': 'Трансформация культуры и обучение', 'price_hint': 'от 200 000 ₽', 'duration': '1 месяц', 'deliverables': ['План обучения', 'Система мотивации'], 'case_study': 'Finance клиент: +300% AI-инициатив.'},
    '3': {'service': 'Аудит инфраструктуры и AI Governance', 'price_hint': 'от 150 000 ₽', 'duration': '2 недели', 'deliverables': ['Отчет готовности', 'Оценка TCO'], 'case_study': 'Manufacturing: -30% облачных расходов.'},
    '4': {'service': 'Экспресс-аудит данных (Data Quality)', 'price_hint': 'от 180 000 ₽', 'duration': '3 недели', 'deliverables': ['Data Quality отчет', 'Архитектура Data Lake'], 'case_study': 'Healthcare: ускорение обучения моделей в 2 раза.'},
    '5': {'service': 'MLOps и промышленная эксплуатация', 'price_hint': 'от 250 000 ₽', 'duration': '1 месяц', 'deliverables': ['CI/CD для ML', 'Мониторинг дрейфа'], 'case_study': 'IT клиент: релиз моделей с 3 мес до 2 недель.'},
    '6': {'service': 'Запуск AI-пилотов (Quick Wins)', 'price_hint': 'от 300 000 ₽', 'duration': '1.5 месяца', 'deliverables': ['2-3 прототипа', 'Оценка бизнес-эффекта'], 'case_study': 'Services: экономия 2000 часов/год.'},
    '7': {'service': 'R&D лаборатория и партнерства', 'price_hint': 'от 150 000 ₽', 'duration': '1 месяц', 'deliverables': ['Карта партнеров', 'Бюджет R&D'], 'case_study': 'Telecom: грант на совместную разработку.'}
}



DIMENSIONS = {
    '1': {'name': 'Стратегия и управление', 'weight': 0.15, 'group': 'governance'},
    '2': {'name': 'Люди и культура', 'weight': 0.15, 'group': 'people'},
    '3': {'name': 'Инфраструктура', 'weight': 0.15, 'group': 'tech'},
    '4': {'name': 'Данные', 'weight': 0.15, 'group': 'tech'},
    '5': {'name': 'Модели', 'weight': 0.15, 'group': 'tech'},
    '6': {'name': 'Внедрение ИИ', 'weight': 0.20, 'group': 'execution'},
    '7': {'name': 'Исследования (R&D)', 'weight': 0.05, 'group': 'rd'},
}


# Оси фокуса: рекомендации по этим осям паттерн продвигает в начало списка.
PATTERN_FOCUS: Dict[str, List[str]] = {
    'compressed_circle': ['1', '3'],
    'people_anchor': ['2'],
    'right_skew': ['2'],
    'left_skew': ['6'],
    'benchmark_parity': ['7'],
    'star_with_gaps': [],
    'single_anchor': [],
    'balanced': [],
}


def get_pattern_focus_axes(
    pattern: Optional[PatternInfo],
    dimension_scores: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Оси, которые паттерн продвигает в начало рекомендаций."""
    if not pattern:
        return []
    ptype = pattern.pattern_type
    if ptype == 'star_with_gaps' and dimension_scores:
        return [k for k, v in dimension_scores.items() if v <= 2.0][:2]
    if ptype == 'single_anchor' and dimension_scores:
        return [max(dimension_scores, key=lambda k: dimension_scores[k])]
    return list(PATTERN_FOCUS.get(ptype, []))


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

    # Якорь: одна ось значительно выше остальных при слабом фоне
    top = max(scores)
    top_idx = scores.index(top) + 1
    others_avg = _avg(sorted(scores, reverse=True)[1:])
    if top - others_avg > 1.2 and others_avg < 2.6:
        if top_idx == 2:
            return PatternInfo(
                pattern_type='people_anchor',
                diagnosis='Сильная команда при системном отставании',
                recommendation=(
                    'Ваша опора — люди и культура. Используйте вовлечённую команду как двигатель '
                    'трансформации: начните с быстрых ИИ-пилотов (quick wins), параллельно выстраивая '
                    'стратегию и инфраструктуру.'
                ),
                severity='warning',
            )
        return PatternInfo(
            pattern_type='single_anchor',
            diagnosis=f'Локальная сила: {DIM_NAMES[str(top_idx)]}',
            recommendation=(
                f'Ось «{DIM_NAMES[str(top_idx)]}» заметно сильнее остальных. '
                'Опирайтесь на неё: выстраивайте смежные процессы от сильной стороны.'
            ),
            severity='warning',
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
    """Generate upsell triggers based on dimension scores using templates."""
    triggers = []
    
    # Сортируем оси по оценке (от худшей к лучшей)
    focus = get_pattern_focus_axes(pattern, dimension_scores)
    sorted_dims = sorted(dimension_scores.items(), key=lambda kv: (0 if kv[0] in focus else 1, kv[1]))
    
    # Берем только те, где оценка < 3.5 (зоны роста)
    for dim_id, score in sorted_dims:
        if score < 3.5 and dim_id in UPSELL_TEMPLATES:
            template = UPSELL_TEMPLATES[dim_id]
            triggers.append({
                'type': 'critical_bottleneck' if score < 2.5 else 'growth_zone',
                'dimension_id': dim_id,
                'dimension_name': DIM_NAMES.get(dim_id, f'Ось {dim_id}'),
                'score': score,
                'risk': f"Оценка {score:.1f}/5.0. {template['case_study']}",
                'service': template['service'],
                'price_hint': template['price_hint'],
                'duration': template['duration'],
                'deliverables': template['deliverables'],
                'case_study': template['case_study']
            })
            if len(triggers) >= 3: # Ограничиваем топ-3 триггерами
                break
                
    return triggers
