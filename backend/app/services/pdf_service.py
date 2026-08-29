"""Professional PDF Report Generation Service using WeasyPrint.
v3 «Аудит»: фирменный стиль лендинга (бумага/чернила/зелёный, IBM Plex),
колонтитулы и номера страниц на каждой странице (CSS Paged Media),
увеличенный кегль, страница 2 заполнена методикой и планом 90 дней.
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
    'it': 'IT', 'retail': 'Ритейл', 'finance': 'Финансы и банки',
    'manufacturing': 'Производство', 'services': 'Услуги',
    'healthcare': 'Здравоохранение', 'education': 'Образование',
    'government': 'Госсектор', 'other': 'Другое', 'crossindustry': 'Кросс-отраслевой',
    'ecommerce': 'E-commerce', 'fintech': 'Финтех', 'telecom': 'Телеком',
    'logistics': 'Логистика', 'energy': 'Энергетика', 'construction': 'Строительство и девелопмент',
}

SIZE_MAP = {
    'small': 'малый бизнес', 'medium': 'средний бизнес',
    'large': 'крупный бизнес', 'enterprise': 'корпорация',
}

REPORT_TYPE_MAP = {
    'express': 'Экспресс-отчёт', 'executive': 'Executive-отчёт', 'comprehensive': 'Полный отчёт',
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
        ('Выбрать 2-3 use case с быстрым измеримым эффектом', 'AI Lead', '30 дней'),
        ('Построить baseline-модель или выбрать vendor-решение', 'AI Lead', '60 дней'),
        ('Настроить мониторинг точности и дрейфа', 'MLOps', '90 дней'),
    ],
    '6': [
        ('Запустить 2-3 ИИ-пилота с бизнес-владельцами', 'Бизнес-владелец', '6-8 недель'),
        ('Определить критерии успеха пилотов в деньгах и времени', 'CEO', '30 дней'),
        ('Внедрить ежемесячное ревью ИИ-инициатив', 'CEO', 'постоянно'),
    ],
    '7': [
        ('Установить партнёрство с 1-2 университетами', 'R&D Lead', '60 дней'),
        ('Подать заявку на 1 грант в квартал', 'R&D Lead', 'ежеквартально'),
        ('Публиковать 1 кейс или статью в полугодие', 'R&D + Marketing', '6 месяцев'),
    ],
}

SEVERITY_ACCENT = {'critical': '#b42318', 'warning': '#b45309', 'info': '#0d6b4f', 'success': '#0d6b4f'}


def get_industry(audit_data: Dict) -> str:
    industry = (
        audit_data.get('request', {}).get('company_industry', '') or
        audit_data.get('company_profile', {}).get('industry', '') or
        audit_data.get('company_industry', '')
    )
    if not industry:
        return 'Не указана'
    return INDUSTRY_MAP.get(industry.lower().strip(), industry.capitalize())


def get_size(audit_data: Dict) -> str:
    size = (
        audit_data.get('request', {}).get('company_size', '') or
        audit_data.get('company_profile', {}).get('size', '') or ''
    )
    return SIZE_MAP.get(size.lower().strip(), '')


def get_report_type(audit_data: Dict) -> str:
    rt = audit_data.get('report_type', '') or 'express'
    return REPORT_TYPE_MAP.get(rt.lower().strip(), rt.capitalize())


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
    return 'уровень native: ИИ является ядром бизнес-модели'


def generate_radar_svg(current: Dict, benchmark: Optional[Dict] = None,
                       target: Optional[Dict] = None, size: int = 262) -> str:
    """Радар в фирменной палитре: сетка/подписи чернила, бенчмарк серый пунктир,
    цель зелёный пунктир, профиль чернильный контур, критичные оси красные точки."""
    cx = cy = size / 2
    R = size * 0.335
    names = [DIM_META[str(i + 1)]['short'] for i in range(7)]

    def pt(i: int, v: float):
        ang = math.radians(-90 + i * 360 / 7)
        r = R * max(0.0, min(5.0, v)) / 5.0
        return cx + r * math.cos(ang), cy + r * math.sin(ang)

    parts = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    for lv in (1, 2, 3, 4, 5):
        pts = ' '.join(f'{pt(i, lv)[0]:.1f},{pt(i, lv)[1]:.1f}' for i in range(7))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="#c6cbc2" stroke-width="1"/>')
    for i in range(7):
        x, y = pt(i, 5)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#c6cbc2" stroke-width="1"/>')
        lx, ly = pt(i, 6.15)
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{max(9, size // 26)}" fill="#15181b" '
                     f'text-anchor="middle" font-weight="600" font-family="IBM Plex Sans">{names[i]}</text>')

    def poly(vals, color, fill_op, dash=''):
        pts = ' '.join(f'{pt(i, vals[i])[0]:.1f},{pt(i, vals[i])[1]:.1f}' for i in range(7))
        d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<polygon points="{pts}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="2"{d}/>'

    if benchmark:
        parts.append(poly([float(benchmark.get(str(i + 1), 0)) for i in range(7)], '#a8ada4', 0.0, '4 3'))
    if target:
        parts.append(poly([float(target.get(str(i + 1), 0)) for i in range(7)], '#0d6b4f', 0.0, '2 2'))
    parts.append(poly([float(current.get(str(i + 1), 0)) for i in range(7)], '#23282d', 0.10))
    for i in range(7):
        if float(current.get(str(i + 1), 0)) <= 1.8:
            x, y = pt(i, float(current.get(str(i + 1), 0)))
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#b42318" stroke="#fff" stroke-width="1.5"/>')
    parts.append('</svg>')
    return ''.join(parts)


def generate_speedometer_svg(score: float, max_score: float = 5.0) -> str:
    """Совместимость со старыми вызовами."""
    return ''


CSS = """
@page {
  size: A4;
  margin: 20mm 12mm 17mm;
  @top-left {
    content: element(runhead);
    width: 100%;
    vertical-align: bottom;
    border-bottom: 1px solid #dcded6;
    margin-bottom: 4mm;
  }
  @bottom-left {
    content: "© 2026 NetBrainPower · Методика: магистерская диссертация РАНХиГС · Конфиденциально";
    font-family: 'IBM Plex Sans'; font-size: 7.5px; color: #565d63;
    vertical-align: top; padding-top: 2mm;
  }
  @bottom-right {
    content: "Стр. " counter(page) " из " counter(pages);
    font-family: 'IBM Plex Mono'; font-size: 7.5px; font-weight: 600; color: #565d63;
    vertical-align: top; padding-top: 2mm;
  }
}
.runhead {
  position: running(pagehead);
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 9px; padding-bottom: 2.5mm;
}
.runhead .logo { font-size: 11.5px; font-weight: 700; letter-spacing: -0.02em; color: #15181b; }
.runhead .logo em { font-style: normal; color: #0d6b4f; }
.runhead .cap { font-family: 'IBM Plex Mono'; font-size: 7.5px; font-weight: 600;
  letter-spacing: 0.12em; text-transform: uppercase; color: #565d63; }
body { font-family: 'IBM Plex Sans'; color: #15181b; font-size: 10.5px; line-height: 1.45; margin: 0; }
.mono, .num { font-family: 'IBM Plex Mono'; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
h1 { font-size: 21px; font-weight: 600; letter-spacing: -0.02em; margin: 6px 0 3px; }
.meta { color: #565d63; font-size: 8.5px; }
.score-row { display: flex; align-items: baseline; gap: 10px; margin: 10px 0 6px; }
.big { font-family: 'IBM Plex Mono'; font-size: 37px; font-weight: 600; letter-spacing: -0.03em; }
.of { color: #565d63; font-size: 11.5px; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 2px; font-size: 9.5px; font-weight: 600; }
h2 { font-size: 12px; font-weight: 600; margin: 14px 0 6px; padding-bottom: 3px; border-bottom: 1px solid #dcded6; }
.tk { display: flex; gap: 9px; padding: 5px 0; border-bottom: 1px solid #ecece8; }
.tk .n { font-family: 'IBM Plex Mono'; color: #0d6b4f; font-size: 10px; font-weight: 600; }
.tk b { font-weight: 600; }
.cols { display: flex; gap: 13px; margin-top: 5px; }
.left { width: 47%; text-align: center; }
.right { width: 53%; }
.legend { font-size: 8px; color: #565d63; margin-top: 3px; line-height: 1.35; }
.diag { border: 1px solid #dcded6; border-left: 3px solid #0d6b4f; border-radius: 2px; padding: 8px 10px; background: #f8f8f6; }
.diag .t { font-weight: 600; color: #0a5640; font-size: 11px; margin-bottom: 3px; }
.diag .d { font-size: 9.5px; }
.kv { display: flex; justify-content: space-between; border-bottom: 1px solid #ecece8; padding: 4px 0; font-size: 9.5px; }
.kv span:last-child { font-family: 'IBM Plex Mono'; font-weight: 600; }
table { width: 100%; border-collapse: collapse; font-size: 9px; }
th { text-align: left; color: #565d63; font-size: 7.5px; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1.5px solid #15181b; padding: 4px 5px; font-weight: 600; }
td { padding: 4.5px 5px; border-bottom: 1px solid #ecece8; vertical-align: top; }
td.num, .num { font-family: 'IBM Plex Mono'; font-weight: 600; }
td.dim { color: #565d63; font-weight: 400; }
td.neg { color: #b42318; }
td.pos { color: #0d6b4f; }
td.interp { color: #565d63; }
.bar { background: #eceae4; height: 4.5px; width: 56px; border-radius: 1px; }
.bar div { height: 4.5px; border-radius: 1px; }
.m3 { margin-top: 4px; }
.mtable td { font-size: 9.5px; padding: 5px; }
.mtable td:first-child { font-weight: 600; width: 24%; }
.scale { display: flex; margin: 5px 0 2px; }
.scale div { flex: 1; text-align: center; padding: 6px 2px; font-size: 8.5px; font-weight: 600; }
.scale div span { display: block; font-family: 'IBM Plex Mono'; font-weight: 400; font-size: 7.5px; margin-top: 1px; }
.grid3 { display: flex; margin-top: 5px; }
.prio { width: 33.3%; padding: 2px 12px 2px 0; }
.prio + .prio { border-left: 1px solid #dcded6; padding-left: 12px; }
.prio .pn { font-family: 'IBM Plex Mono'; font-size: 22px; font-weight: 400; color: #0d6b4f; line-height: 1; }
.prio .ph { font-size: 10.5px; font-weight: 600; margin: 3px 0 1px; }
.prio .pv { font-size: 8.5px; color: #565d63; margin-bottom: 5px; }
.prio .pv .up { color: #0d6b4f; font-weight: 600; }
.prio ol { margin: 0; padding-left: 13px; }
.prio li { margin: 5px 0; font-size: 9px; }
.prio .ow { display: block; color: #565d63; font-size: 8.5px; }
.note { background: #e6efe9; border: 1px solid #9dbfac; border-radius: 2px; padding: 8px 11px;
  font-size: 9px; color: #0a5640; margin-top: 12px; }
.note ol { margin: 4px 0 0; padding-left: 16px; }
.note li { margin: 2px 0; }
.cta { background: #0d6b4f; color: #fff; border-radius: 2px; padding: 12px 14px; text-align: center; margin-top: 14px; }
.cta b { font-size: 12px; }
.cta .ln { font-family: 'IBM Plex Mono'; font-size: 9.5px; margin-top: 3px; }
.cta .sm { font-size: 8px; color: #d9e8e0; margin-top: 4px; }
"""


def generate_pdf_report(audit_data: Dict) -> bytes:
    indices = audit_data.get('calculated_indices', {})
    dimension_scores = {k: float(v) for k, v in indices.get('dimension_scores', {}).items()}
    composite = float(indices.get('composite_score', 0))
    maturity_level = indices.get('maturity_level', 'Начальный')
    pattern = indices.get('pattern', {})
    benchmark_scores = indices.get('benchmark_scores') or {}
    target_scores = audit_data.get('request', {}).get('target_scores')
    audit_id = str(audit_data.get('audit_id', 'N/A'))[:8]
    industry = get_industry(audit_data)
    size_label = get_size(audit_data)
    rt_label = get_report_type(audit_data)
    date_str = datetime.now().strftime('%d.%m.%Y')
    level_info = MATURITY_LEVELS.get(maturity_level, MATURITY_LEVELS['Начальный'])
    tco = indices.get('tco_estimate_millions')

    scores = {i: dimension_scores.get(i, 0.0) for i in DIM_ORDER}
    strong = max(scores, key=scores.get)
    weak = min(scores, key=scores.get)
    gaps = {i: scores[i] - float(benchmark_scores.get(i, 0)) for i in DIM_ORDER} if benchmark_scores else {}
    gap_axis = min(gaps, key=gaps.get) if gaps else None
    below_bench = sum(1 for g in gaps.values() if g < -0.1) if gaps else 0

    takeaways = [
        f"<b>Сильная сторона: {DIM_META[strong]['name']}, {scores[strong]:.1f} из 5.</b> Опора для трансформации.",
        f"<b>Зона роста №1: {DIM_META[weak]['name']}, {scores[weak]:.1f} из 5.</b> Главный приоритет инвестиций.",
    ]
    if gap_axis is not None and gaps[gap_axis] < -0.3:
        takeaways.append(
            f"<b>Разрыв с отраслью: {DIM_META[gap_axis]['name']}, {scores[gap_axis]:.1f} при бенчмарке "
            f"{float(benchmark_scores.get(gap_axis, 0)):.1f}.</b> Отрасль ушла вперёд на {abs(gaps[gap_axis]):.1f} балла."
        )
    else:
        takeaways.append(f"<b>Общий уровень: {maturity_level}, {composite:.2f} из 5.</b> {_band_phrase(composite).split(': ', 1)[-1]}.")

    gap_line = ''
    if gap_axis is not None:
        gap_line = f"<div class='kv'><span>Наибольший разрыв</span><span>{DIM_META[gap_axis]['short']}, {gaps[gap_axis]:+.1f}</span></div>"

    radar = generate_radar_svg(dimension_scores, benchmark_scores or None, target_scores)

    rows = []
    for i in DIM_ORDER:
        s = scores[i]
        b = float(benchmark_scores.get(i, 0)) if benchmark_scores else None
        gap_txt = f"{s - b:+.1f}" if b is not None else "-"
        gap_cls = 'neg' if (b is not None and s - b < 0) else 'pos'
        interp = _band_phrase(s)
        if b is not None:
            interp += '; ниже среднего по отрасли' if s - b < -0.4 else ('; выше среднего по отрасли' if s - b > 0.4 else '; вблизи среднего')
        rows.append(
            f"<tr><td><strong>{DIM_META[i]['name']}</strong></td>"
            f"<td><div class='bar'><div style='width:{s / 5 * 100:.0f}%;background:{_bar_color(s)}'></div></div></td>"
            f"<td class='num'>{s:.1f}</td><td class='num dim'>{b if b is not None else '-'}</td>"
            f"<td class='num {gap_cls}'>{gap_txt}</td><td class='interp'>{interp}</td></tr>"
        )
    axes_table = (
        "<table><tr><th>Ось</th><th>Профиль</th><th>Балл</th><th>Бенч.</th><th>Разрыв</th><th>Интерпретация</th></tr>"
        + "".join(rows) + "</table>"
    )

    method_rows = "".join(
        f"<tr><td>{DIM_META[i]['short']}</td><td>{DIM_META[i]['desc']}</td></tr>"
        for i in DIM_ORDER
    )
    scale_cells = "".join(
        f"<div style='background:{v['color']};color:{v['text']};'>{k}<span>{v['min']:.1f}-{v['max']:.1f}</span></div>"
        for k, v in MATURITY_LEVELS.items()
    )

    weak3 = sorted(scores, key=scores.get)[:3]
    plan_cols = []
    for n, wid in enumerate(weak3, 1):
        steps = "".join(
            f"<li><strong>{what}</strong><span class='ow'>{owner}, {term}</span></li>"
            for what, owner, term in ACTION_STEPS[wid]
        )
        if target_scores and str(target_scores.get(wid)):
            tgt = float(target_scores.get(wid))
            pv = f"<div class='pv'><span class='num'>{scores[wid]:.1f}</span> → цель {tgt:.1f} <span class='up'>(+{tgt - scores[wid]:.1f})</span></div>"
        else:
            pv = f"<div class='pv'><span class='num'>{scores[wid]:.1f}</span> из 5.00</div>"
        plan_cols.append(
            f"<div class='prio'><div class='pn'>{n}</div>"
            f"<div class='ph'>{DIM_META[wid]['name']}</div>{pv}<ol>{steps}</ol></div>"
        )

    tco_html = f"<span class='of' style='margin-left:auto;'>TCO ИИ-ландшафта: {tco:.1f} млн ₽</span>" if tco else ''

    html = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>

<div class="runhead">
  <div class="logo">NetBrain<em>Power</em></div>
  <div class="cap">Индекс ИИ-зрелости · Отчёт об оценке · {date_str}</div>
</div>

<div class="page">
  <h1>Индекс ИИ-зрелости компании</h1>
  <div class="meta">Отрасль: {industry}{', ' + size_label if size_label else ''} · 35 критериев, 7 осей · {rt_label} · ID {audit_id}</div>
  <div class="score-row">
    <span class="big">{composite:.2f}</span><span class="of">/ 5.00</span>
    <span class="badge" style="background:{level_info['color']};color:{level_info['text']};">{maturity_level}</span>
    {tco_html}
  </div>

  <h2>Три главных вывода</h2>
  {''.join(f"<div class='tk'><span class='n'>0{i+1}</span><div>{t}</div></div>" for i, t in enumerate(takeaways))}

  <h2>Радар зрелости и диагноз</h2>
  <div class="cols">
    <div class="left">{radar}
      <div class="legend">Чёрный контур: ваш профиль · серый пунктир: бенчмарк отрасли · зелёный: цель · красные точки: критичные оси</div>
    </div>
    <div class="right">
      <div class="diag" style="border-left-color:{SEVERITY_ACCENT.get(pattern.get('severity', 'info'), '#0d6b4f')};">
        <div class="t">Диагноз: {pattern.get('diagnosis', '-')}</div>
        <div class="d">{pattern.get('recommendation', '')}</div>
      </div>
      <div style="margin-top:8px;">
        <div class="kv"><span>Целевое состояние задано</span><span>{len(target_scores) if target_scores else 0} осей</span></div>
        <div class="kv"><span>Осей ниже бенчмарка</span><span>{below_bench} из 7</span></div>
        {gap_line}
      </div>
    </div>
  </div>

  <h2>Анализ по 7 осям зрелости</h2>
  {axes_table}
  <div class="meta m3">Бенчмарк: средние значения по отрасли «{industry}» в базе исследования. Шкала 1-5.</div>
</div>

<div class="page">
  <h2 style="margin-top:0;">Методика оценки</h2>
  <table class="mtable">
    {method_rows}
  </table>
  <div class="meta" style="margin-top:5px;font-weight:600;color:#15181b;">Шкала уровней зрелости</div>
  <div class="scale">{scale_cells}</div>

  <h2>План действий на 90 дней</h2>
  <div class="meta" style="margin-bottom:3px;">Три приоритета: оси с наименьшими оценками. Для каждого: шаги, владелец, срок и целевой уровень через 12 месяцев.</div>
  <div class="grid3">{''.join(plan_cols)}</div>
  <div class="note"><b>Как измерять успех.</b> По каждому шагу зафиксируйте метрику до старта и сверяйтесь ежемесячно:
    <ol>
      <li>число ИИ-пилотов, дошедших до продакшена;</li>
      <li>доля сотрудников, прошедших обучение ИИ-грамотности;</li>
      <li>доля ИИ-бюджета, утверждённая отдельной статьёй.</li>
    </ol>
  </div>

  <div class="cta">
    <b>Хотите обсудить результаты с экспертом?</b>
    <div class="ln">netbrainpower.ru · ИИ-стратегия, пилоты и трансформация с измеримым ROI</div>
    <div class="sm">Поделитесь отчётом с коллегами: решение о трансформации принимается командой</div>
  </div>
</div>
</body></html>"""

    return HTML(string=html).write_pdf()
