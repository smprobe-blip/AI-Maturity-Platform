"""PDF Report Generation Service using fpdf2."""

import os
from datetime import datetime
from typing import Dict, Any, List

from fpdf import FPDF
import structlog

logger = structlog.get_logger()


# Названия измерений
DIMENSION_NAMES = {
    "1": "Стратегия и видение",
    "2": "Данные и инфраструктура",
    "3": "Технологии и инструменты",
    "4": "Кадры и компетенции",
    "5": "Процессы и управление",
    "6": "Культура и изменения",
    "7": "Этика и ответственность",
}

# Путь к шрифту с кириллицей (DejaVu в Debian)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class AuditReportPDF(FPDF):
    """Custom PDF class for audit reports."""
    
    def __init__(self):
        super().__init__()
        # Добавляем шрифт с кириллицей
        if os.path.exists(FONT_PATH):
            self.add_font("DejaVu", "", FONT_PATH, uni=True)
            self.add_font("DejaVu", "B", FONT_BOLD_PATH, uni=True)
            self.default_font = "DejaVu"
        else:
            self.default_font = "Helvetica"
            logger.warning("dejavu_font_not_found", path=FONT_PATH)
    
    def header(self):
        self.set_font(self.default_font, "B", 18)
        self.set_text_color(102, 126, 234)
        self.cell(0, 15, "AI Maturity Assessment", 0, 1, "C")
        self.set_font(self.default_font, "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Отчёт по оценке зрелости искусственного интеллекта", 0, 1, "C")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font(self.default_font, "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"AI Maturity Platform | Страница {self.page_no()}/{{nb}}", 0, 0, "C")
    
    def section_title(self, title: str):
        self.ln(5)
        self.set_font(self.default_font, "B", 14)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, title, 0, 1, "L")
        self.set_draw_color(102, 126, 234)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
    
    def info_box(self, data: Dict[str, str]):
        """Blue info box with company details."""
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        self.set_font(self.default_font, "B", 14)
        self.cell(0, 12, f"  {data.get('company_name', 'N/A')}", 0, 1, "L", fill=True)
        
        self.set_font(self.default_font, "", 10)
        items = [
            f"Отрасль: {data.get('industry', 'N/A')}",
            f"Размер компании: {data.get('company_size', 'N/A')}",
            f"ID аудита: {data.get('audit_id', 'N/A')}",
            f"Дата проведения: {data.get('audit_date', 'N/A')}",
        ]
        for item in items:
            self.cell(0, 7, f"  {item}", 0, 1, "L", fill=True)
        self.ln(5)
    
    def score_block(self, score: float, level: str):
        """Big score display."""
        self.set_fill_color(240, 240, 240)
        self.rect(10, self.get_y(), 190, 40, style="F")
        
        self.set_font(self.default_font, "B", 36)
        self.set_text_color(102, 126, 234)
        self.set_y(self.get_y() + 5)
        self.cell(0, 18, f"{score:.1f}", 0, 1, "C")
        
        self.set_font(self.default_font, "B", 12)
        self.set_text_color(118, 75, 162)
        self.cell(0, 8, level, 0, 1, "C")
        
        self.set_font(self.default_font, "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Композитная оценка зрелости ИИ", 0, 1, "C")
        self.ln(8)
    
    def dimension_table(self, dimension_scores: Dict[str, float]):
        """Table of dimension scores."""
        self.set_font(self.default_font, "B", 10)
        self.set_fill_color(230, 230, 250)
        self.set_text_color(0, 0, 0)
        
        self.cell(120, 8, "Измерение", 1, 0, "C", fill=True)
        self.cell(40, 8, "Оценка", 1, 0, "C", fill=True)
        self.cell(30, 8, "Из 5.0", 1, 1, "C", fill=True)
        
        self.set_font(self.default_font, "", 10)
        self.set_fill_color(248, 249, 250)
        
        row_index = 0
        for dim_id in ["1", "2", "3", "4", "5", "6", "7"]:
            score = dimension_scores.get(dim_id, 0)
            name = DIMENSION_NAMES.get(dim_id, f"Измерение {dim_id}")
            
            fill = row_index % 2 == 0
            self.set_text_color(0, 0, 0)
            self.cell(120, 8, f"  {name}", 1, 0, "L", fill=fill)
            
            self.set_text_color(102, 126, 234)
            self.set_font(self.default_font, "B", 10)
            self.cell(40, 8, f"{score:.1f}", 1, 0, "C", fill=fill)
            
            self.set_font(self.default_font, "", 9)
            self.set_text_color(100, 100, 100)
            self.cell(30, 8, "/ 5.0", 1, 1, "C", fill=fill)
            
            self.set_font(self.default_font, "", 10)
            row_index += 1
        self.ln(5)
    
    def business_metrics(self, roi: float, tco: float):
        """Business value metrics."""
        self.set_fill_color(240, 248, 255)
        
        self.set_font(self.default_font, "B", 20)
        self.set_text_color(102, 126, 234)
        
        # ROI
        self.cell(95, 20, f"{roi}%", 1, 0, "C", fill=True)
        self.set_x(115)
        # TCO
        self.cell(95, 20, f"{tco} млн ₽", 1, 1, "C", fill=True)
        
        self.set_font(self.default_font, "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(95, 6, "Ожидаемый ROI", 0, 0, "C")
        self.set_x(115)
        self.cell(95, 6, "Оценка TCO (3 года)", 0, 1, "C")
        self.ln(5)
    
    def recommendations_list(self, recommendations: List[Dict[str, str]]):
        """List of recommendations."""
        self.set_font(self.default_font, "", 10)
        self.set_text_color(0, 0, 0)
        
        for rec in recommendations:
            self.set_fill_color(248, 249, 250)
            self.set_draw_color(118, 75, 162)
            
            # Рамка слева
            y = self.get_y()
            self.set_line_width(0.8)
            self.line(10, y, 10, y + 15)
            self.set_line_width(0.2)
            
            # Текст
            self.set_x(13)
            self.set_font(self.default_font, "B", 10)
            self.set_text_color(118, 75, 162)
            self.multi_cell(187, 6, f"{rec.get('priority', '')}", 0, "L")
            
            self.set_x(13)
            self.set_font(self.default_font, "", 9)
            self.set_text_color(60, 60, 60)
            self.multi_cell(187, 5, rec.get("text", ""), 0, "L")
            self.ln(2)


class PDFReportService:
    """Service for generating PDF reports."""
    
    def generate_audit_report(self, audit_data: Dict[str, Any]) -> bytes:
        """Generate PDF report for an audit."""
        logger.info("generating_pdf_report", audit_id=audit_data.get("audit_id"))
        
        # Извлекаем данные
        company_profile = audit_data.get("company_profile", {})
        calculated_indices = audit_data.get("calculated_indices", {})
        dimension_scores = calculated_indices.get("dimension_scores", {})
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(dimension_scores)
        
        # Создаём PDF
        pdf = AuditReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Блок информации о компании
        pdf.info_box({
            "company_name": company_profile.get("company_name", "Не указано"),
            "industry": company_profile.get("industry", "Не указано"),
            "company_size": company_profile.get("company_size", "Не указано"),
            "audit_id": audit_data.get("audit_id", "N/A")[:16] + "...",
            "audit_date": str(audit_data.get("created_at", "N/A"))[:10],
        })
        
        # Блок с оценкой
        pdf.section_title("Общая оценка зрелости")
        pdf.score_block(
            score=calculated_indices.get("composite_score", 0),
            level=calculated_indices.get("maturity_level", "N/A"),
        )
        
        # Таблица измерений
        pdf.section_title("Оценки по 7 измерениям")
        pdf.dimension_table(dimension_scores)
        
        # Бизнес-метрики
        pdf.section_title("Оценка бизнес-эффекта")
        pdf.business_metrics(
            roi=calculated_indices.get("roi_estimate_percent", 0),
            tco=calculated_indices.get("tco_estimate_millions", 0),
        )
        
        # Рекомендации
        pdf.section_title("Ключевые рекомендации")
        pdf.recommendations_list(recommendations)
        
        # Получаем PDF как bytes
        # fpdf2 возвращает bytearray, конвертируем в bytes
        pdf_bytes = bytes(pdf.output(dest='S'))
        
        logger.info("pdf_report_generated",
                   audit_id=audit_data.get("audit_id"),
                   size_bytes=len(pdf_bytes))
        
        return pdf_bytes
    
    def _generate_recommendations(self, dimension_scores: Dict[str, float]) -> List[Dict[str, str]]:
        """Generate recommendations based on dimension scores."""
        recommendations = []
        
        priority_map = {
            "1": "Разработайте чёткую AI-стратегию, согласованную с бизнес-целями компании",
            "2": "Инвестируйте в качество данных и построение единой data-платформы",
            "3": "Внедрите современные MLOps-практики и автоматизацию ML-пайплайнов",
            "4": "Запустите программу обучения сотрудников работе с AI-инструментами",
            "5": "Формализуйте процессы управления AI-проектами и их метрики",
            "6": "Сформируйте культуру data-driven принятия решений на всех уровнях",
            "7": "Внедрите этический кодекс использования AI и систему governance",
        }
        
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
        
        priority = 1
        for dim_id, score in sorted_dims:
            if score < 4.0 and priority <= 3:
                recommendations.append({
                    "priority": f"Приоритет {priority}",
                    "text": f"{DIMENSION_NAMES[dim_id]} (оценка: {score:.1f}). {priority_map[dim_id]}"
                })
                priority += 1
        
        if not recommendations:
            recommendations.append({
                "priority": "Следующий шаг",
                "text": "Высокий уровень зрелости. Сфокусируйтесь на масштабировании успешных AI-инициатив и трансфере знаний между подразделениями."
            })
        
        return recommendations


pdf_service = PDFReportService()
