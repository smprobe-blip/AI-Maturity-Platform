"""
Professional PDF Report Generation Service using WeasyPrint.
Без эмодзи — только SVG-иконки для 100% надёжного рендеринга.
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

DIMENSION_NAMES = {
    '1': 'Стратегия', '2': 'Люди', '3': 'Инфра',
    '4': 'Данные', '5': 'Модели', '6': 'Внедрение', '7': 'R&D',
}

# SVG-иконки вместо эмодзи
DIMENSION_ICONS = {
    '1': '<circle cx="12" cy="12" r="10" fill="#3B82F6"/><path d="M12 6v6l4 2" stroke="white" stroke-width="2" fill="none"/>',
    '2': '<circle cx="8" cy="8" r="3" fill="#10B981"/><circle cx="16" cy="8" r="3" fill="#10B981"/><path d="M6 18c0-2 2-3 4-3h4c2 0 4 1 4 3" stroke="#10B981" stroke-width="2" fill="none"/>',
    '3': '<circle cx="12" cy="12" r="4" fill="#6B7280"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1" stroke="#6B7280" stroke-width="2"/>',
    '4': '<rect x="3" y="3" width="18" height="18" rx="2" fill="#8B5CF6"/><path d="M7 14l3-3 3 3 4-4" stroke="white" stroke-width="2" fill="none"/>',
    '5': '<rect x="4" y="4" width="16" height="16" rx="3" fill="#EF4444"/><circle cx="9" cy="10" r="2" fill="white"/><circle cx="15" cy="10" r="2" fill="white"/><path d="M8 15c1 1 3 1 4 0s3-1 4 0" stroke="white" stroke-width="1.5" fill="none"/>',
    '6': '<path d="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 4 2-7L2 9h7z" fill="#F59E0B"/>',
    '7': '<circle cx="12" cy="12" r="3" fill="#EC4899"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l2.5 2.5M16.5 16.5L19 19M5 19l2.5-2.5M16.5 7.5L19 5" stroke="#EC4899" stroke-width="2"/>',
}

DIM_ORDER = ['1', '2', '3', '4', '5', '6', '7']

INDUSTRY_MAP = {
    'it': 'IT', 'retail': 'Retail', 'finance': 'Finance',
    'manufacturing': 'Manufacturing', 'services': 'Services',
    'healthcare': 'Healthcare', 'education': 'Education',
    'government': 'Government', 'other': 'Другое', 'crossindustry': 'Кросс-отраслевой'
}


def get_industry(audit_data: Dict) -> str:
    industry = (
        audit_data.get('request', {}).get('company_industry', '') or
        audit_data.get('company_profile', {}).get('industry', '') or
        audit_data.get('company_industry', '')
    )
    if not industry:
        return 'Не указана'
    clean_industry = industry.lower().strip()
    return INDUSTRY_MAP.get(clean_industry, industry.capitalize())


def icon_svg(dim_id: str, size: int = 24) -> str:
    """Возвращает SVG-иконку для оси."""
    icon_content = DIMENSION_ICONS.get(dim_id, '<circle cx="12" cy="12" r="10" fill="#9CA3AF"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 6px;">{icon_content}</svg>'


def section_icon_svg(icon_type: str) -> str:
    """Иконки для заголовков разделов."""
    icons = {
        'summary': '<circle cx="12" cy="12" r="10" fill="#3B82F6"/><path d="M8 12l3 3 5-6" stroke="white" stroke-width="2" fill="none"/>',
        'radar': '<circle cx="12" cy="12" r="10" fill="none" stroke="#3B82F6" stroke-width="2"/><circle cx="12" cy="12" r="6" fill="none" stroke="#3B82F6" stroke-width="2"/><circle cx="12" cy="12" r="2" fill="#3B82F6"/>',
        'services': '<path d="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 4 2-7L2 9h7z" fill="#F59E0B"/>',
    }
    content = icons.get(icon_type, '')
    return f'<svg width="28" height="28" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 8px;">{content}</svg>'


def generate_score_bar(score: float, max_score: float = 5.0) -> str:
    percentage = (score / max_score) * 100
    if score <= 1.8: color = '#EF4444'
    elif score <= 2.6: color = '#F59E0B'
    elif score <= 3.4: color = '#10B981'
    elif score <= 4.2: color = '#3B82F6'
    else: color = '#8B5CF6'
    
    return f"""
    <div style="background: #F3F4F6; border-radius: 4px; height: 8px; overflow: hidden; margin: 4px 0;">
        <div style="background: {color}; width: {percentage:.0f}%; height: 100%; border-radius: 4px;"></div>
    </div>
    """


def generate_radar_svg(current: Dict[str, float], benchmark: Optional[Dict[str, float]], target: Optional[Dict[str, float]]) -> str:
    """Радар зрелости без эмодзи."""
    target = target or {str(i): 4.0 for i in range(1, 8)}
    
    width, height = 500, 620
    cx, cy = width / 2, height / 2 - 40
    radius = 180
    max_score = 5.0
    n = len(DIM_ORDER)
    angle_step = 2 * math.pi / n
    
    def get_point(dim_idx: int, score: float) -> tuple:
        angle = angle_step * dim_idx - math.pi / 2
        r = (score / max_score) * radius
        return cx + r * math.cos(angle), cy + r * math.sin(angle)
    
    svg = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="margin: 20px auto; display: block;">']
    
    # Фоновые концентрические зоны
    zones = [
        (1.8, '#FEE2E2', 0.8), (2.6, '#FEF3C7', 0.8), (3.4, '#DCFCE7', 0.8),
        (4.2, '#DBEAFE', 0.8), (5.0, '#EDE9FE', 0.8),
    ]
    for zone_max, color, opacity in reversed(zones):
        r = (zone_max / max_score) * radius
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{opacity}"/>')
    
    # Оси и подписи
    for i, dim_id in enumerate(DIM_ORDER):
        x, y = get_point(i, max_score)
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#9CA3AF" stroke-width="1.5"/>')
        lx, ly = get_point(i, max_score + 0.5)
        svg.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="middle" font-size="13" font-weight="700" fill="#1F2937">{DIMENSION_NAMES[dim_id]}</text>')
    
    # Бенчмарк
    if benchmark:
        pts = [get_point(i, benchmark.get(dim, 0)) for i, dim in enumerate(DIM_ORDER)]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        svg.append(f'<polygon points="{pts_str}" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-dasharray="6,4"/>')
        for x, y in pts:
            svg.append(f'<path d="M {x-6} {y} L {x} {y-6} L {x+6} {y} L {x} {y+6} Z" fill="#9CA3AF" stroke="white" stroke-width="1.5"/>')
    
    # Целевое
    pts_target = [get_point(i, target.get(dim, 0)) for i, dim in enumerate(DIM_ORDER)]
    pts_target_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts_target)
    svg.append(f'<polygon points="{pts_target_str}" fill="none" stroke="#10B981" stroke-width="2.5" stroke-dasharray="6,4"/>')
    
    # Текущее
    pts_current = [get_point(i, current.get(dim, 0)) for i, dim in enumerate(DIM_ORDER)]
    pts_current_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts_current)
    svg.append(f'<polygon points="{pts_current_str}" fill="rgba(59, 130, 246, 0.15)" stroke="#3B82F6" stroke-width="3"/>')
    for x, y in pts_current:
        svg.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#EF4444" stroke="white" stroke-width="2.5"/>')
        svg.append(f'<circle cx="{x}" cy="{y}" r="3" fill="white"/>')
    
    # Легенда
    legend_y = 30
    legend_items = [
        ('#3B82F6', '', 'Текущее'),
        ('#10B981', '6,4', 'Целевое'),
        ('#9CA3AF', '6,4', 'Бенчмарк'),
    ]
    for i, (color, dash, label) in enumerate(legend_items):
        ly = legend_y + i * 22
        svg.append(f'<line x1="30" y1="{ly}" x2="60" y2="{ly}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>')
        svg.append(f'<text x="70" y="{ly}" dominant-baseline="middle" font-size="12" fill="#374151" font-weight="600">{label}</text>')
    
    # Шкала уровней
    scale_y = cy + radius + 60
    scale_width = 420
    scale_height = 20
    scale_x = (width - scale_width) / 2
    
    svg.append('<defs><linearGradient id="maturityGradient" x1="0%" y1="0%" x2="100%" y2="0%">')
    svg.append('<stop offset="0%" style="stop-color:#FEE2E2;stop-opacity:1" />')
    svg.append('<stop offset="20%" style="stop-color:#FEF3C7;stop-opacity:1" />')
    svg.append('<stop offset="40%" style="stop-color:#DCFCE7;stop-opacity:1" />')
    svg.append('<stop offset="60%" style="stop-color:#DBEAFE;stop-opacity:1" />')
    svg.append('<stop offset="80%" style="stop-color:#EDE9FE;stop-opacity:1" />')
    svg.append('<stop offset="100%" style="stop-color:#EDE9FE;stop-opacity:1" />')
    svg.append('</linearGradient></defs>')
    
    svg.append(f'<rect x="{scale_x}" y="{scale_y}" width="{scale_width}" height="{scale_height}" rx="10" fill="url(#maturityGradient)" stroke="#E5E7EB" stroke-width="1"/>')
    
    level_names = ['Начальный', 'AI-Enabled', 'AI-Driven', 'AI-First', 'AI-Native']
    level_ranges = ['1.0-1.8', '1.9-2.6', '2.7-3.4', '3.5-4.2', '4.3-5.0']
    for i, (name, range_text) in enumerate(zip(level_names, level_ranges)):
        x = scale_x + (i + 0.5) * (scale_width / 5)
        svg.append(f'<text x="{x}" y="{scale_y + 35}" text-anchor="middle" font-size="11" fill="#1F2937" font-weight="700">{name}</text>')
        svg.append(f'<text x="{x}" y="{scale_y + 50}" text-anchor="middle" font-size="9" fill="#6B7280">{range_text}</text>')
    
    svg.append('</svg>')
    return '\n'.join(svg)


def generate_speedometer_svg(score: float, max_score: float = 5.0) -> str:
    percentage = score / max_score
    if score <= 1.8: color = '#EF4444'
    elif score <= 2.6: color = '#F59E0B'
    elif score <= 3.4: color = '#10B981'
    elif score <= 4.2: color = '#3B82F6'
    else: color = '#8B5CF6'
    
    end_x = 20 + 160 * percentage
    return f"""
    <svg width="200" height="120" viewBox="0 0 220 130" style="margin: 10px auto; display: block;">
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#E5E7EB" stroke-width="16" stroke-linecap="round"/>
        <path d="M 20 100 A 80 80 0 0 1 {end_x:.1f} 100" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round"/>
        <text x="100" y="95" text-anchor="middle" font-size="26" font-weight="bold" fill="{color}" font-family="DejaVu Sans, Arial, sans-serif">{score:.2f}</text>
        <text x="100" y="112" text-anchor="middle" font-size="10" fill="#6B7280" font-family="DejaVu Sans, Arial, sans-serif">/ {max_score:.2f}</text>
    </svg>
    """


def generate_pdf_report(audit_data: Dict) -> bytes:
    indices = audit_data.get('calculated_indices', {})
    dimension_scores = indices.get('dimension_scores', {})
    composite_score = indices.get('composite_score', 0)
    maturity_level = indices.get('maturity_level', 'Начальный')
    pattern = indices.get('pattern', {})
    upsell_triggers = audit_data.get('upsell_triggers', [])
    recommendations = audit_data.get('recommendations', [])
    audit_id = audit_data.get('audit_id', 'N/A')
    
    industry = get_industry(audit_data)
    target_scores = audit_data.get('request', {}).get('target_scores')
    benchmark_scores = indices.get('benchmark_scores')
    
    level_info = MATURITY_LEVELS.get(maturity_level, MATURITY_LEVELS['Начальный'])
    
    # Цветной индикатор уровня
    level_indicator = f'<span style="display: inline-block; width: 16px; height: 16px; border-radius: 50%; background: {level_info["text"]}; vertical-align: middle; margin-right: 6px;"></span>'
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4; margin: 1.5cm; }}
            @page :first {{ margin: 0; }}
            body {{ 
                font-family: 'DejaVu Sans', Arial, sans-serif; 
                font-size: 10.5pt; 
                line-height: 1.4; 
                color: #1F2937; 
                margin: 0; padding: 0; 
            }}
            .cover {{ 
                background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); 
                color: white; text-align: center; 
                padding: 80px 40px; min-height: 267mm; 
                display: flex; flex-direction: column; justify-content: center; 
                page-break-after: always; 
            }}
            .cover h1 {{ font-size: 32pt; font-weight: bold; margin: 0 0 15px 0; }}
            .cover .subtitle {{ font-size: 14pt; opacity: 0.9; margin: 0 0 40px 0; }}
            .cover .meta {{ font-size: 11pt; opacity: 0.85; line-height: 1.8; }}
            
            .section {{ margin: 15px 0; page-break-inside: avoid; }}
            .section h2 {{ 
                font-size: 15pt; color: #1E40AF; 
                border-bottom: 2px solid #E5E7EB; 
                padding-bottom: 6px; margin-bottom: 15px;
                display: flex; align-items: center;
            }}
            .section h3 {{ font-size: 12pt; color: #374151; margin: 15px 0 8px 0; font-weight: 600; }}
            
            .score-card {{ 
                background: #F9FAFB; border: 1px solid #E5E7EB; 
                border-radius: 8px; padding: 15px; margin: 10px 0; text-align: center; 
            }}
            .score-card .score {{ 
                font-size: 36pt; font-weight: bold; color: #1E40AF; 
                margin: 0; line-height: 1; 
                font-family: 'DejaVu Sans', Arial, sans-serif;
            }}
            .score-card .level {{ font-size: 13pt; color: #6B7280; margin: 6px 0 0 0; }}
            
            .dim-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 10px 0; }}
            .dim-card {{ 
                background: white; border: 1px solid #E5E7EB; 
                border-radius: 6px; padding: 10px 12px; 
            }}
            .dim-card .header {{ display: flex; align-items: center; margin-bottom: 4px; }}
            .dim-card .name {{ font-weight: 600; font-size: 10pt; color: #1F2937; }}
            .dim-card .score {{ 
                font-size: 16pt; font-weight: bold; color: #1E40AF; 
                margin: 4px 0; line-height: 1;
                font-family: 'DejaVu Sans', Arial, sans-serif;
            }}
            
            .pattern-box {{ 
                background: {level_info['color']}; 
                border-left: 3px solid {level_info['text']}; 
                padding: 12px 15px; border-radius: 6px; margin: 10px 0; 
            }}
            .pattern-box .diagnosis {{ font-size: 12pt; font-weight: bold; color: {level_info['text']}; margin: 0 0 6px 0; }}
            .pattern-box p {{ margin: 0; font-size: 10pt; }}
            
            .upsell-card {{ 
                background: white; border: 1px solid #BFDBFE; 
                border-radius: 8px; padding: 15px; margin: 10px 0; 
                page-break-inside: avoid;
            }}
            .upsell-card .service {{ font-size: 12pt; font-weight: bold; color: #1E40AF; margin: 0 0 10px 0; }}
            .upsell-card .meta {{ display: flex; gap: 12px; margin: 10px 0; font-size: 9.5pt; }}
            .upsell-card .meta-item {{ background: #EFF6FF; padding: 5px 10px; border-radius: 4px; }}
            .upsell-card .meta-item .label {{ color: #6B7280; font-size: 8.5pt; }}
            .upsell-card .meta-item .value {{ font-weight: bold; color: #1F2937; }}
            .upsell-card .deliverables {{ margin: 10px 0 0 0; padding-left: 18px; font-size: 9.5pt; }}
            .upsell-card .deliverables li {{ margin: 4px 0; color: #374151; }}
            .case-box {{ background: #F0FDF4; padding: 8px 10px; border-radius: 4px; margin-top: 10px; font-size: 9.5pt; }}
            
            ul {{ margin: 6px 0; padding-left: 20px; }}
            li {{ margin: 5px 0; font-size: 10pt; }}
            
            .footer {{ 
                text-align: center; color: #9CA3AF; font-size: 8.5pt; 
                margin-top: 20px; padding-top: 10px; border-top: 1px solid #E5E7EB; 
            }}
        </style>
    </head>
    <body>
        <div class="cover">
            <h1>Отчёт об оценке зрелости ИИ</h1>
            <div class="subtitle">AI Maturity Assessment Report</div>
            <div class="meta">
                <div>ID аудита: {audit_id}</div>
                <div>Дата: {datetime.now().strftime('%d.%m.%Y')}</div>
                <div>Отрасль: {industry}</div>
                <div style="margin-top: 30px; font-size: 12pt;">AI Maturity Platform</div>
            </div>
        </div>
        
        <div class="section">
            <h2>{section_icon_svg('summary')} Сводка результатов</h2>
            <div class="score-card">
                <div class="score">{composite_score:.2f} / 5.00</div>
                <div class="level">Уровень зрелости: {level_indicator} {maturity_level}</div>
            </div>
            {generate_speedometer_svg(composite_score)}
            
            <h3>Оценки по осям</h3>
            <div class="dim-grid">
    """
    
    for dim_id in DIM_ORDER:
        score = dimension_scores.get(dim_id, 0)
        html += f"""
                <div class="dim-card">
                    <div class="header">
                        {icon_svg(dim_id, 24)}
                        <span class="name">{DIMENSION_NAMES.get(dim_id, dim_id)}</span>
                    </div>
                    <div class="score">{score:.1f}</div>
                    {generate_score_bar(score)}
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>""" + section_icon_svg('radar') + """ Радар зрелости</h2>
    """
    html += generate_radar_svg(dimension_scores, benchmark_scores, target_scores)
    
    if pattern:
        html += f"""
                <h3>Диагноз</h3>
                <div class="pattern-box">
                    <div class="diagnosis">{pattern.get('diagnosis', '') or pattern.get('name', '')}</div>
                    <p>{pattern.get('recommendation', '') or pattern.get('description', '')}</p>
                </div>
        """
    
    if recommendations:
        html += "<h3>Ключевые рекомендации</h3><ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
    
    html += "</div>"
    
    if upsell_triggers:
        html += """
        <div class="section" style="page-break-before: always;">
            <h2>""" + section_icon_svg('services') + """ Рекомендуемые услуги</h2>
            <p style="color: #6B7280; font-size: 9.5pt; margin-bottom: 15px;">На основе результатов вашего аудита мы рекомендуем следующие услуги:</p>
        """
        for trigger in upsell_triggers[:3]:
            html += f"""
                <div class="upsell-card">
                    <div class="service">{trigger.get('service', '')}</div>
                    <div class="meta">
                        <div class="meta-item"><div class="label">Срок</div><div class="value">{trigger.get('duration', '')}</div></div>
                        <div class="meta-item"><div class="label">Инвестиции</div><div class="value">{trigger.get('price_hint', '')}</div></div>
                    </div>
            """
            if trigger.get('deliverables'):
                html += '<div style="margin: 8px 0;"><strong>Результаты:</strong><ul class="deliverables">'
                for item in trigger['deliverables']:
                    html += f"<li>{item}</li>"
                html += "</ul></div>"
            if trigger.get('case_study'):
                html += f'<div class="case-box"><strong>Кейс:</strong> {trigger["case_study"]}</div>'
            html += "</div>"
        html += "</div>"
    
    html += f"""
        <div class="footer">
            <div style="font-size: 10pt; color: #1E40AF; margin-bottom: 6px; font-weight: bold;">AI Maturity Platform</div>
            <div>Конфиденциально • {datetime.now().strftime('%d.%m.%Y')}</div>
            <div style="margin-top: 10px; font-size: 8pt; color: #9CA3AF;">Отчёт подготовлен на основе предоставленных данных. Рекомендации носят консультационный характер.</div>
        </div>
    </body>
    </html>
    """
    
    return HTML(string=html).write_pdf()
