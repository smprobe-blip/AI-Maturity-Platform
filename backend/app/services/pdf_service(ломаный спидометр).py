"""
Professional PDF Report Generation Service using WeasyPrint.
Упрощенная графика для корректного рендеринга.
"""
from datetime import datetime
from typing import Dict, Optional
from weasyprint import HTML

MATURITY_LEVELS = {
    'Начальный': {'color': '#FEE2E2', 'text': '#7F1D1D', 'range': '1.0-1.8'},
    'AI-Enabled': {'color': '#FEF3C7', 'text': '#78350F', 'range': '1.9-2.6'},
    'AI-Driven': {'color': '#DCFCE7', 'text': '#14532D', 'range': '2.7-3.4'},
    'AI-First': {'color': '#DBEAFE', 'text': '#1E3A8A', 'range': '3.5-4.2'},
    'AI-Native': {'color': '#EDE9FE', 'text': '#4C1D95', 'range': '4.3-5.0'},
}

DIMENSION_NAMES = {
    '1': 'Стратегия', '2': 'Люди', '3': 'Инфра',
    '4': 'Данные', '5': 'Модели', '6': 'Внедрение', '7': 'R&D',
}

DIMENSION_ICONS = {
    '1': '🎯', '2': '', '3': '⚙️', '4': '📊',
    '5': '🤖', '6': '', '7': '🔬',
}

DIM_ORDER = ['1', '2', '3', '4', '5', '6', '7']

def get_industry(audit_data: Dict) -> str:
    req = audit_data.get('request', {}) or {}
    profile = audit_data.get('company_profile', {}) or {}
    industry = req.get('company_industry', '') or profile.get('industry', '') or audit_data.get('company_industry', '')
    if not industry:
        return 'Не указана'
    clean = str(industry).lower().strip()
    mapping = {
        'it': 'IT', 'retail': 'Retail', 'finance': 'Finance',
        'manufacturing': 'Manufacturing', 'services': 'Services',
        'healthcare': 'Healthcare', 'education': 'Education',
        'government': 'Government', 'other': 'Другое'
    }
    return mapping.get(clean, str(industry).capitalize())

def generate_score_bar(score: float, max_score: float = 5.0) -> str:
    pct = (score / max_score) * 100
    color = '#EF4444' if score <= 1.8 else '#F59E0B' if score <= 2.6 else '#10B981' if score <= 3.4 else '#3B82F6' if score <= 4.2 else '#8B5CF6'
    return '<div style="background: #F3F4F6; border-radius: 4px; height: 8px; overflow: hidden; margin: 4px 0;"><div style="background: %s; width: %.0f%%; height: 100%%; border-radius: 4px;"></div></div>' % (color, pct)

def generate_speedometer_html(score: float, max_score: float = 5.0) -> str:
    zones = [
        ('#EF4444', '1.0'),
        ('#F59E0B', '1.9'),
        ('#10B981', '2.7'),
        ('#3B82F6', '3.5'),
        ('#8B5CF6', '4.3'),
    ]
    needle_color = '#EF4444'
    for color, label in zones:
        if float(label) <= score < float(label) + 0.9:
            needle_color = color
            break
    pct = max(0, min(100, ((score - 1.0) / 4.0) * 100))
    
    html = '<div style="text-align: center; margin: 20px 0;">'
    html += '<div style="position: relative; width: 300px; height: 30px; margin: 0 auto; border-radius: 15px; overflow: hidden;">'
    html += '<div style="position: absolute; left: 0%; width: 20%; height: 100%; background: #EF4444;"></div>'
    html += '<div style="position: absolute; left: 20%; width: 20%; height: 100%; background: #F59E0B;"></div>'
    html += '<div style="position: absolute; left: 40%; width: 20%; height: 100%; background: #10B981;"></div>'
    html += '<div style="position: absolute; left: 60%; width: 20%; height: 100%; background: #3B82F6;"></div>'
    html += '<div style="position: absolute; left: 80%; width: 20%; height: 100%; background: #8B5CF6;"></div>'
    html += '<div style="position: absolute; left: %.1f%%; top: -5px; width: 4px; height: 40px; background: #1F2937; transform: translateX(-50%%);"></div>' % pct
    html += '<div style="position: absolute; left: %.1f%%; top: -8px; width: 12px; height: 12px; background: %s; border-radius: 50%%; transform: translateX(-50%%); border: 2px solid white;"></div>' % (pct, needle_color)
    html += '</div>'
    html += '<div style="display: flex; justify-content: space-between; width: 300px; margin: 10px auto 0; font-size: 11px;">'
    html += '<span style="color: #EF4444; font-weight: bold;">1.0</span>'
    html += '<span style="color: #F59E0B; font-weight: bold;">1.9</span>'
    html += '<span style="color: #10B981; font-weight: bold;">2.7</span>'
    html += '<span style="color: #3B82F6; font-weight: bold;">3.5</span>'
    html += '<span style="color: #8B5CF6; font-weight: bold;">4.3</span>'
    html += '</div>'
    html += '<div style="margin-top: 20px; font-size: 42px; font-weight: bold; color: %s; font-family: DejaVu Sans, Arial, sans-serif;">%.2f</div>' % (needle_color, score)
    html += '<div style="font-size: 14px; color: #6B7280;">/ %.2f</div>' % max_score
    html += '</div>'
    return html

def generate_radar_html(current: Dict[str, float], benchmark: Optional[Dict[str, float]], target: Optional[Dict[str, float]]) -> str:
    target = target or {str(i): 4.0 for i in range(1, 8)}
    rows = []
    for dim_id in DIM_ORDER:
        dim_name = DIMENSION_NAMES.get(dim_id, dim_id)
        icon = DIMENSION_ICONS.get(dim_id, '')
        curr_score = current.get(dim_id, 0)
        bench_score = benchmark.get(dim_id, 0) if benchmark else 0
        targ_score = target.get(dim_id, 0)
        color = '#EF4444' if curr_score <= 1.8 else '#F59E0B' if curr_score <= 2.6 else '#10B981' if curr_score <= 3.4 else '#3B82F6' if curr_score <= 4.2 else '#8B5CF6'
        rows.append('<tr><td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">%s %s</td><td style="padding: 8px; border-bottom: 1px solid #E5E7EB; text-align: center; font-weight: bold; color: %s;">%.1f</td><td style="padding: 8px; border-bottom: 1px solid #E5E7EB; text-align: center; color: #10B981;">%.1f</td><td style="padding: 8px; border-bottom: 1px solid #E5E7EB; text-align: center; color: #9CA3AF;">%.1f</td></tr>' % (icon, dim_name, color, curr_score, targ_score, bench_score))
    
    html = '<div style="margin: 20px 0;">'
    html += '<table style="width: 100%; border-collapse: collapse; font-size: 11pt;">'
    html += '<thead><tr style="background: #F9FAFB;">'
    html += '<th style="padding: 10px; text-align: left; border-bottom: 2px solid #E5E7EB;">Ось</th>'
    html += '<th style="padding: 10px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #3B82F6;">Текущее</th>'
    html += '<th style="padding: 10px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #10B981;">Целевое</th>'
    html += '<th style="padding: 10px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #9CA3AF;">Бенчмарк</th>'
    html += '</tr></thead><tbody>'
    html += '\n'.join(rows)
    html += '</tbody></table>'
    html += '<div style="margin-top: 20px; padding: 15px; background: #F9FAFB; border-radius: 8px;">'
    html += '<div style="font-weight: bold; margin-bottom: 10px; font-size: 10pt;">Уровни зрелости:</div>'
    html += '<div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 9pt;">'
    html += '<div style="padding: 5px 10px; background: #FEE2E2; border-radius: 4px;"><strong>Начальный:</strong> 1.0-1.8</div>'
    html += '<div style="padding: 5px 10px; background: #FEF3C7; border-radius: 4px;"><strong>AI-Enabled:</strong> 1.9-2.6</div>'
    html += '<div style="padding: 5px 10px; background: #DCFCE7; border-radius: 4px;"><strong>AI-Driven:</strong> 2.7-3.4</div>'
    html += '<div style="padding: 5px 10px; background: #DBEAFE; border-radius: 4px;"><strong>AI-First:</strong> 3.5-4.2</div>'
    html += '<div style="padding: 5px 10px; background: #EDE9FE; border-radius: 4px;"><strong>AI-Native:</strong> 4.3-5.0</div>'
    html += '</div></div></div>'
    return html

def generate_pdf_report(audit_data: Dict) -> bytes:
    idx = audit_data.get('calculated_indices', {})
    dim_scores = idx.get('dimension_scores', {})
    comp_score = idx.get('composite_score', 0)
    mat_level = idx.get('maturity_level', 'Начальный')
    pattern = idx.get('pattern', {})
    upsell = audit_data.get('upsell_triggers', [])
    recs = audit_data.get('recommendations', [])
    audit_id = audit_data.get('audit_id', 'N/A')
    industry = get_industry(audit_data)
    target_scores = audit_data.get('request', {}).get('target_scores')
    benchmark_scores = idx.get('benchmark_scores')
    lvl = MATURITY_LEVELS.get(mat_level, MATURITY_LEVELS['Начальный'])
    lvl_ind = '<span style="display: inline-block; width: 16px; height: 16px; border-radius: 50%; background: %s; vertical-align: middle; margin-right: 6px;"></span>' % lvl["text"]
    
    html = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
    html += '@page { size: A4; margin: 1.5cm; } @page :first { margin: 0; }'
    html += 'body { font-family: DejaVu Sans, Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #1F2937; margin: 0; padding: 0; }'
    html += '.cover { background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); color: white; text-align: center; padding: 80px 40px; min-height: 267mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }'
    html += '.cover h1 { font-size: 32pt; font-weight: bold; margin: 0 0 15px 0; }'
    html += '.cover .subtitle { font-size: 14pt; opacity: 0.9; margin: 0 0 40px 0; }'
    html += '.cover .meta { font-size: 11pt; opacity: 0.85; line-height: 1.8; }'
    html += '.section { margin: 15px 0; page-break-inside: avoid; }'
    html += '.section h2 { font-size: 15pt; color: #1E40AF; border-bottom: 2px solid #E5E7EB; padding-bottom: 6px; margin-bottom: 15px; }'
    html += '.section h3 { font-size: 12pt; color: #374151; margin: 15px 0 8px 0; font-weight: 600; }'
    html += '.score-card { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin: 10px 0; text-align: center; }'
    html += '.score-card .score { font-size: 36pt; font-weight: bold; color: #1E40AF; margin: 0; line-height: 1; }'
    html += '.score-card .level { font-size: 13pt; color: #6B7280; margin: 6px 0 0 0; }'
    html += '.dim-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 10px 0; }'
    html += '.dim-card { background: white; border: 1px solid #E5E7EB; border-radius: 6px; padding: 10px 12px; }'
    html += '.dim-card .header { display: flex; align-items: center; margin-bottom: 4px; font-size: 14pt; }'
    html += '.dim-card .name { font-weight: 600; font-size: 10pt; color: #1F2937; margin-left: 6px; }'
    html += '.dim-card .score { font-size: 16pt; font-weight: bold; color: #1E40AF; margin: 4px 0; line-height: 1; }'
    html += '.pattern-box { background: %s; border-left: 3px solid %s; padding: 12px 15px; border-radius: 6px; margin: 10px 0; }' % (lvl['color'], lvl['text'])
    html += '.pattern-box .diagnosis { font-size: 12pt; font-weight: bold; color: %s; margin: 0 0 6px 0; }' % lvl['text']
    html += '.pattern-box p { margin: 0; font-size: 10pt; }'
    html += '.upsell-card { background: white; border: 1px solid #BFDBFE; border-radius: 8px; padding: 15px; margin: 10px 0; page-break-inside: avoid; }'
    html += '.upsell-card .service { font-size: 12pt; font-weight: bold; color: #1E40AF; margin: 0 0 10px 0; }'
    html += '.upsell-card .meta { display: flex; gap: 12px; margin: 10px 0; font-size: 9.5pt; }'
    html += '.upsell-card .meta-item { background: #EFF6FF; padding: 5px 10px; border-radius: 4px; }'
    html += '.upsell-card .meta-item .label { color: #6B7280; font-size: 8.5pt; }'
    html += '.upsell-card .meta-item .value { font-weight: bold; color: #1F2937; }'
    html += '.upsell-card .deliverables { margin: 10px 0 0 0; padding-left: 18px; font-size: 9.5pt; }'
    html += '.upsell-card .deliverables li { margin: 4px 0; color: #374151; }'
    html += '.case-box { background: #F0FDF4; padding: 8px 10px; border-radius: 4px; margin-top: 10px; font-size: 9.5pt; }'
    html += 'ul { margin: 6px 0; padding-left: 20px; } li { margin: 5px 0; font-size: 10pt; }'
    html += '.footer { text-align: center; color: #9CA3AF; font-size: 8.5pt; margin-top: 20px; padding-top: 10px; border-top: 1px solid #E5E7EB; }'
    html += '</style></head><body>'
    html += '<div class="cover"><h1>Отчёт об оценке зрелости ИИ</h1><div class="subtitle">AI Maturity Assessment Report</div>'
    html += '<div class="meta"><div>ID аудита: %s</div><div>Дата: %s</div><div>Отрасль: %s</div><div style="margin-top: 30px; font-size: 12pt;">AI Maturity Platform</div></div></div>' % (audit_id, datetime.now().strftime('%d.%m.%Y'), industry)
    html += '<div class="section"><h2>📊 Сводка результатов</h2>'
    html += '<div class="score-card"><div class="score">%.2f / 5.00</div><div class="level">Уровень зрелости: %s %s</div></div>' % (comp_score, lvl_ind, mat_level)
    html += generate_speedometer_html(comp_score)
    html += '<h3>Оценки по осям</h3><div class="dim-grid">'
    for dim in DIM_ORDER:
        sc = dim_scores.get(dim, 0)
        html += '<div class="dim-card"><div class="header"><span>%s</span><span class="name">%s</span></div><div class="score">%.1f</div>%s</div>' % (DIMENSION_ICONS.get(dim, ''), DIMENSION_NAMES.get(dim, dim), sc, generate_score_bar(sc))
    html += '</div></div>'
    html += '<div class="section"><h2>🎯 Радар зрелости</h2>'
    html += generate_radar_html(dim_scores, benchmark_scores, target_scores)
    if pattern:
        html += '<h3>Диагноз</h3><div class="pattern-box"><div class="diagnosis">%s</div><p>%s</p></div>' % (pattern.get('diagnosis', '') or pattern.get('name', ''), pattern.get('recommendation', '') or pattern.get('description', ''))
    if recs:
        html += '<h3>Ключевые рекомендации</h3><ul>' + ''.join('<li>%s</li>' % r for r in recs) + '</ul>'
    html += '</div>'
    if upsell:
        html += '<div class="section" style="page-break-before: always;"><h2>🚀 Рекомендуемые услуги</h2><p style="color: #6B7280; font-size: 9.5pt; margin-bottom: 15px;">На основе результатов вашего аудита мы рекомендуем следующие услуги:</p>'
        for tr in upsell[:3]:
            html += '<div class="upsell-card"><div class="service">%s</div><div class="meta"><div class="meta-item"><div class="label">Срок</div><div class="value">%s</div></div><div class="meta-item"><div class="label">Инвестиции</div><div class="value">%s</div></div></div>' % (tr.get('service', ''), tr.get('duration', ''), tr.get('price_hint', ''))
            if tr.get('deliverables'):
                html += '<div style="margin: 8px 0;"><strong>Результаты:</strong><ul class="deliverables">' + ''.join('<li>%s</li>' % it for it in tr['deliverables']) + '</ul></div>'
            if tr.get('case_study'):
                html += '<div class="case-box"><strong>Кейс:</strong> %s</div>' % tr['case_study']
            html += '</div>'
        html += '</div>'
    html += '<div class="footer"><div style="font-size: 10pt; color: #1E40AF; margin-bottom: 6px; font-weight: bold;">AI Maturity Platform</div><div>Конфиденциально • %s</div><div style="margin-top: 10px; font-size: 8pt; color: #9CA3AF;">Отчёт подготовлен на основе предоставленных данных. Рекомендации носят консультационный характер.</div></div>' % datetime.now().strftime('%d.%m.%Y')
    html += '</body></html>'
    return HTML(string=html).write_pdf()
