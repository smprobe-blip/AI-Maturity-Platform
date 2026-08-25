"""Professional PDF Report Generation Service using WeasyPrint.
v2.1: компактный двухстраничный отчёт.
Стр.1: резюме + выводы + радар/диагноз + анализ осей.
Стр.2: методика (в начале) → план 90 дней → мягкий CTA.
Без цен внутри отчёта — CTA на netbrainpower.ru.
"""
import math
from datetime import datetime
from typing import Dict, Optional
from weasyprint import HTML

MATURITY_LEVELS = {
    'Начальный': {'color': '#FEE2E2', 'text': '#7F1D1D', 'min': 1.0, 'max': 1.8},
    'AI-Enabled': {'color': '#FEF3C7', 'text': '#78350F', 'min': 1.9, 'max': 2.6},
    'AI-Driven': {'color': '#DCFCE7', 'text': '#14532D', 'min': 2.7, 'max': 3.4},
    'AI-First': {'color': '#DBEAFE', 'text': '#1E3A8A', 'min': 3.5, 'max': 4.2},
    'AI-Native': {'color': '#EDE9FE', 'text': '#4C1D95', 'min': 4.3, 'max': 5.0},
}

DIM_ORDER = ['1', '2', '3', '4', '5', '6', '7']

DIM_META = {
    '1': {'name': 'Стратегия и управление', 'short': 'Стратегия', 'desc': 'ИИ-видение, роадмап, бюджет, вовлечённость топ-менеджмента'},
    '2': {'name': 'Люди и культура', 'short': 'Люди', 'desc': 'Компетенции, роли, культура экспериментов, change management'},
    '3': {'name': 'Инфраструктура', 'short': 'Инфраструктура', 'desc': 'Вычисления, хранение, MLOps, среды разработки'},
    '4': {'name': 'Данные', 'short': 'Данные', 'desc': 'Качество, доступность, governance, пайплайны данных'},
    '5': {'name': 'Модели', 'short': 'Модели', 'desc': 'ML/LLM-решения, точность, мониторинг, эксплуатация'},
    '6': {'name': 'Внедрение ИИ', 'short': 'Внедрение', 'desc': 'Продакшен-сценарии, ROI, процессы внедрения'},
    '7': {'name': 'Исследования (R&D)', 'short': 'R&D', 'desc': 'Эксперименты, партнёрства, публикации, патенты'},
}

INDUSTRY_MAP = {
    'it': 'IT', 'retail': 'Retail', 'finance': 'Finance',
    'manufacturing': 'Manufacturing', 'services': 'Services',
    'healthcare': 'Healthcare', 'education': 'Education',
    'government': 'Госсектор', 'other': 'Другое', 'crossindustry': 'Кросс-отраслевой',
    'ecommerce': 'E-commerce', 'fintech': 'Финтех', 'telecom': 'Телеком',
    'logistics': 'Логистика', 'energy': 'Энергетика', 'construction': 'Строительство / Девелопмент',
}

ACTION_STEPS = {
    '1': [
        ('Провести ИИ-стратегическую сессию с топ-менеджментом', 'CEO', '2 дня'),
        ('Утвердить роадмап на 12 мес с 3 измеримыми целями', 'Стратег-блок', '30 дней'),
        ('Закрепить ИИ-бюджет отдельной статьёй', 'CFO', '60 дней'),
    ],
    '2': [
        ('Назначить AI-чемпионов в каждом подразделении', 'HRD', '30 дней'),
        ('Запустить курс ИИ-грамотности для 20% сотрудников', 'L&D', '60 дней'),
        ('Включить ИИ-инициативы в KPI руководителей', 'CEO', '90 дней'),
    ],
    '3': [
        ('Провести аудит вычислительных ресурсов и облачных затрат', 'CTO', '30 дней'),
        ('Развернуть dev-среду для ИИ-пилотов', 'CTO', '60 дней'),
        ('Утвердить политику безопасности ИИ-инструментов', 'CISO', '90 дней'),
    ],
    '4': [
        ('Определить топ-3 самых ценных дата-активов', 'CDO', '30 дней'),
        ('Назначить владельцев данных и метрики качества', 'CDO', '60 дней'),
        ('Построить пилотный пайплайн с мониторингом качества', 'Data Lead', '90 дней'),
    ],
    '5': [
        ('Выбрать 2–3 use case с быстрым измеримым эффектом', 'AI Lead', '30 дней'),
        ('Построить baseline-модель или выбрать vendor-решение', 'AI Lead', '60 дней'),
        ('Настроить мониторинг точности и дрейфа', 'MLOps', '90 дней'),
    ],
    '6': [
        ('Запустить 2–3 ИИ-пилота с бизнес-владельцами', 'Бизнес-владелец', '6–8 нед.'),
        ('Определить критерии успеха пилотов в деньгах/времени', 'CEO', '30 дней'),
        ('Внедрить ежемесячное ревью ИИ-инициатив', 'CEO', 'постоянно'),
    ],
    '7': [
        ('Установить партнёрство с 1–2 университетами', 'R&D Lead', '60 дней'),
        ('Подать заявку на 1 грант в квартал', 'R&D Lead', 'ежеквартально'),
        ('Публиковать 1 кейс/статью в полугодие', 'R&D + Marketing', '6 мес'),
    ],
}

SEVERITY_COLORS = {'critical': '#DC2626', 'warning': '#D97706', 'info': '#2563EB', 'success': '#059669'}


def get_industry(audit_data: Dict) -> str:
    industry = (
        audit_data.get('request', {}).get('company_industry', '') or
        audit_data.get('company_profile', {}).get('industry', '') or
        audit_data.get('company_industry', '')
    )
    if not industry:
        return 'Не указана'
    return INDUSTRY_MAP.get(industry.lower().strip(), industry.capitalize())


def _bar_color(score: float) -> str:
    if score <= 1.8: return '#EF4444'
    if score <= 2.6: return '#F59E0B'
    if score <= 3.4: return '#10B981'
    if score <= 4.2: return '#3B82F6'
    return '#8B5CF6'


def _band_phrase(score: float) -> str:
    if score <= 1.8: return 'начальный уровень: процессы стихийные, системного подхода нет'
    if score <= 2.6: return 'уровень enabled: есть отдельные инициативы, но нет системы'
    if score <= 3.4: return 'уровень driven: процессы стандартизированы и управляются'
    if score <= 4.2: return 'уровень first: ИИ встроен в ключевые бизнес-процессы'
    return 'уровень native: ИИ — ядро бизнес-модели'


def generate_radar_svg(current: Dict, benchmark: Optional[Dict] = None,
                       target: Optional[Dict] = None, size: int = 230) -> str:
    cx = cy = size / 2
    R = size * 0.34
    names = [DIM_META[str(i + 1)]['short'] for i in range(7)]

    def pt(i: int, v: float):
        ang = math.radians(-90 + i * 360 / 7)
        r = R * max(0.0, min(5.0, v)) / 5.0
        return cx + r * math.cos(ang), cy + r * math.sin(ang)

    parts = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    for level in (1, 2, 3, 4, 5):
        pts = ' '.join(f'{pt(i, level)[0]:.1f},{pt(i, level)[1]:.1f}' for i in range(7))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="#E5E7EB" stroke-width="1"/>')
    for i in range(7):
        x, y = pt(i, 5)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        lx, ly = pt(i, 6.1)
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{max(8, size // 28)}" fill="#374151" text-anchor="middle" font-weight="bold">{names[i]}</text>')

    def poly(vals, color, fill_op, dash=''):
        pts = ' '.join(f'{pt(i, vals[i])[0]:.1f},{pt(i, vals[i])[1]:.1f}' for i in range(7))
        d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<polygon points="{pts}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="2"{d}/>'

    if benchmark:
        parts.append(poly([float(benchmark.get(str(i + 1), 0)) for i in range(7)], '#9CA3AF', 0.0, '4 3'))
    if target:
        parts.append(poly([float(target.get(str(i + 1), 0)) for i in range(7)], '#10B981', 0.0, '2 2'))
    parts.append(poly([float(current.get(str(i + 1), 0)) for i in range(7)], '#2563EB', 0.18))
    parts.append('</svg>')
    return ''.join(parts)


def generate_speedometer_svg(score: float, max_score: float = 5.0) -> str:
    """Совместимость со старыми вызовами."""
    return ''


CSS = """
@page { size: A4; margin: 10mm 10mm; }
body { font-family: Helvetica, Arial, sans-serif; color: #111827; font-size: 9.5px; line-height: 1.35; }
.page { page-break-after: always; }
h1 { font-size: 17px; margin: 0 0 2px; }
h2 { font-size: 12px; color: #1D4ED8; border-bottom: 2px solid #2563EB; padding-bottom: 3px; margin: 10px 0 6px; }
h3 { font-size: 10.5px; margin: 8px 0 3px; }
.big { font-size: 26px; font-weight: 800; color: #1D4ED8; }
.of { font-size: 12px; color: #6B7280; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 10px; font-weight: 700; font-size: 10px; }
.muted { color: #6B7280; font-size: 8.5px; }
table { width: 100%; border-collapse: collapse; font-size: 8.5px; }
th, td { padding: 3px 4px; border-bottom: 1px solid #E5E7EB; text-align: left; vertical-align: top; }
th { color: #6B7280; font-size: 8px; text-transform: uppercase; }
.bar { background: #E5E7EB; border-radius: 3px; height: 5px; width: 55px; }
.bar div { height: 5px; border-radius: 3px; }
.diag { padding: 7px 9px; border-radius: 6px; border-left: 4px solid; margin: 6px 0; }
.cta { background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 8px; text-align: center; margin-top: 8px; }
ul.tight, ol.tight { margin: 4px 0; padding-left: 14px; }
ul.tight li, ol.tight li { margin: 2px 0; }
.col-left { float: left; width: 45%; text-align: center; }
.col-right { float: right; width: 53%; }
.clear { clear: both; }
.head { display: flex; justify-content: space-between; align-items: baseline; }
"""


def generate_pdf_report(audit_data: Dict) -> bytes:
    indices = audit_data.get('calculated_indices', {})
    dimension_scores = {k: float(v) for k, v in indices.get('dimension_scores', {}).items()}
    composite = float(indices.get('composite_score', 0))
    maturity_level = indices.get('maturity_level', 'Начальный')
    pattern = indices.get('pattern', {})
    benchmark_scores = indices.get('benchmark_scores') or {}
    target_scores = audit_data.get('request', {}).get('target_scores')
    audit_id = audit_data.get('audit_id', 'N/A')
    industry = get_industry(audit_data)
    date_str = datetime.now().strftime('%d.%m.%Y')
    level_info = MATURITY_LEVELS.get(maturity_level, MATURITY_LEVELS['Начальный'])
    sev_color = SEVERITY_COLORS.get(pattern.get('severity', 'info'), '#2563EB')

    scores = {i: dimension_scores.get(i, 0.0) for i in DIM_ORDER}
    strong = max(scores, key=scores.get)
    weak = min(scores, key=scores.get)
    gaps = {i: scores[i] - float(benchmark_scores.get(i, 0)) for i in DIM_ORDER} if benchmark_scores else {}
    gap_axis = min(gaps, key=gaps.get) if gaps else None

    takeaways = [
        f"<strong>Сильная сторона:</strong> {DIM_META[strong]['name']} — {scores[strong]:.1f}/5. Опора для трансформации.",
        f"<strong>Зона роста №1:</strong> {DIM_META[weak]['name']} — {scores[weak]:.1f}/5. Главный приоритет инвестиций.",
    ]
    if gap_axis is not None and gaps[gap_axis] < -0.3:
        takeaways.append(
            f"<strong>Разрыв с отраслью:</strong> {DIM_META[gap_axis]['name']} — {gaps[gap_axis]:+.1f} к бенчмарку. Отрасль уже ушла вперёд."
        )
    else:
        takeaways.append(f"<strong>Общий уровень:</strong> {maturity_level} ({composite:.2f}/5).")

    radar = generate_radar_svg(dimension_scores, benchmark_scores or None, target_scores)

    # --- Таблица осей (стр. 1) ---
    rows = []
    for i in DIM_ORDER:
        s = scores[i]
        b = float(benchmark_scores.get(i, 0)) if benchmark_scores else None
        gap_txt = f"{s - b:+.1f}" if b is not None else "—"
        interp = _band_phrase(s)
        if b is not None:
            interp += "; ниже среднего по отрасли" if s - b < -0.4 else ("; выше среднего по отрасли" if s - b > 0.4 else "; вблизи среднего")
        rows.append(
            f"<tr><td><strong>{DIM_META[i]['name']}</strong></td>"
            f"<td><div class='bar'><div style='width:{s / 5 * 100:.0f}%;background:{_bar_color(s)}'></div></div></td>"
            f"<td><strong>{s:.1f}</strong></td><td>{b if b is not None else '—'}</td><td>{gap_txt}</td>"
            f"<td>{interp}</td></tr>"
        )
    axes_table = (
        "<table><tr><th>Ось</th><th>Оценка</th><th>Балл</th><th>Бенч.</th><th>Разрыв</th><th>Интерпретация</th></tr>"
        + "".join(rows) + "</table>"
    )

    # --- Методика (стр. 2, в начале) ---
    method_rows = "".join(
        f"<tr><td><strong>{DIM_META[i]['short']}</strong></td><td>{DIM_META[i]['desc']}</td></tr>"
        for i in DIM_ORDER
    )
    scale_cells = "".join(
        f"<td style='background:{v['color']};color:{v['text']};font-weight:700;text-align:center;padding:4px;'>"
        f"{k}<br/>{v['min']:.1f}–{v['max']:.1f}</td>"
        for k, v in MATURITY_LEVELS.items()
    )

    # --- План 90 дней (стр. 2) ---
    weak3 = sorted(scores, key=scores.get)[:3]
    plan_blocks = []
    for n, wid in enumerate(weak3, 1):
        steps = "".join(
            f"<li><strong>{what}</strong> — {owner}, {term}</li>"
            for what, owner, term in ACTION_STEPS[wid]
        )
        plan_blocks.append(
            f"<h3>Приоритет {n}: {DIM_META[wid]['name']} ({scores[wid]:.1f}/5)</h3><ol class='tight'>{steps}</ol>"
        )

    html = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>

<!-- СТРАНИЦА 1: РЕЗЮМЕ + АНАЛИЗ ОСЕЙ -->
<div class="page">
  <div class="head">
    <div class="muted">ИНДЕКС ИИ-ЗРЕЛОСТИ • ОТЧЁТ ОБ ОЦЕНКЕ</div>
    <div class="muted">{date_str}</div>
  </div>
  <h1>Индекс ИИ-зрелости вашей компании</h1>
  <div class="muted">Отрасль: {industry} • Методика: 7 осей, 35 критериев • ID: {audit_id}</div>

  <div style="margin:6px 0;">
    <span class="big">{composite:.2f}</span><span class="of"> / 5.00</span>
    <span class="badge" style="background:{level_info['color']};color:{level_info['text']};margin-left:8px;">{maturity_level}</span>
  </div>

  <h2>Три главных вывода</h2>
  <ul class="tight">{''.join(f'<li>{t}</li>' for t in takeaways)}</ul>

  <h2>Радар зрелости и диагноз</h2>
  <div class="col-left">{radar}
    <div class="muted">Синий — ваш профиль;<br/>серый пунктир — средний по отрасли</div>
  </div>
  <div class="col-right">
    <div class="diag" style="border-color:{sev_color};background:{sev_color}11;">
      <strong style="color:{sev_color};">Диагноз: {pattern.get('diagnosis', '—')}</strong><br/>
      {pattern.get('recommendation', '')}
    </div>
  </div>
  <div class="clear"></div>

  <h2>Анализ по 7 осям зрелости</h2>
  {axes_table}
  <p class="muted" style="margin-top:4px;">Бенчмарк — средние значения по отрасли «{industry}» в базе исследования.</p>
</div>

<!-- СТРАНИЦА 2: МЕТОДИКА → ПЛАН 90 ДНЕЙ → CTA -->
<div class="page">
  <h2>Методика оценки</h2>
  <table><tr><th style="width:22%;">Ось</th><th>Что измеряем</th></tr>{method_rows}</table>
  <h3>Шкала уровней зрелости</h3>
  <table><tr>{scale_cells}</tr></table>

  <h2>План действий на 90 дней</h2>
  <p style="margin:0 0 4px;">Три приоритета — оси с наименьшими оценками. По каждому: шаги, владелец и срок.</p>
  {''.join(plan_blocks)}
  <div class="diag" style="border-color:#059669;background:#05966911;">
    <strong style="color:#059669;">Как измерять успех:</strong> по каждому шагу зафиксируйте метрику до старта
    (число пилотов в проде, доля обученных сотрудников, доля утверждённого бюджета) и сверяйтесь ежемесячно.
  </div>

  <div class="cta">
    <strong>Хотите обсудить результаты с экспертом?</strong><br/>
    netbrainpower.ru — ИИ-стратегия, пилоты и трансформация с измеримым ROI.<br/>
    <span class="muted">Поделитесь отчётом с коллегами — решение о трансформации принимается командой.</span>
  </div>
  <p class="muted" style="margin-top:6px;">
    Отчёт подготовлен автоматически на основе предоставленных ответов и носит консультационный характер.
    Методика разработана в рамках магистерской диссертации РАНХиГС. Конфиденциально.
  </p>
</div>

</body></html>"""

    return HTML(string=html).write_pdf()
