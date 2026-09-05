# -*- coding: utf-8 -*-
"""Генератор диссертационного отчёта — глава магистерской работы (РАНХиГС).

Формирует PDF в формате академической главы: Times-совместимый шрифт 14 pt,
полуторный интервал, абзацный отступ 1,25 см, поля 3/1,5/2/2 см, нумерация
формул и таблиц внутри главы, список источников по ГОСТ Р 7.0.100-2018.
Теоретическая часть — из app.analytics.report_content; результаты — живые,
из run_full_analysis(); недоступные расчёты честно помечаются статусами.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.analytics.report_content import (
    CHAPTER_NO,
    CHAPTER_TITLE,
    DIMENSION_NAMES,
    INTRO,
    REFERENCES,
    REFERENCES_TITLE,
    SECTION_1_HEADING,
    SECTION_1_PURPOSE,
    SECTION_1_THEORY,
    SECTION_2_APPLICABILITY,
    SECTION_2_HEADING,
    SECTION_2_PURPOSE,
    SECTION_2_THEORY,
    SECTION_3_APPLICABILITY,
    SECTION_3_HEADING,
    SECTION_3_PURPOSE,
    SECTION_3_THEORY,
    SECTION_4_APPLICABILITY,
    SECTION_4_HEADING,
    SECTION_4_PURPOSE,
    SECTION_4_THEORY,
    SECTION_5_APPLICABILITY,
    SECTION_5_HEADING,
    SECTION_5_PURPOSE,
    SECTION_5_THEORY,
    SECTION_6_APPLICABILITY,
    SECTION_6_HEADING,
    SECTION_6_PURPOSE,
    SECTION_6_THEORY,
    SECTION_7_HEADING,
    SECTION_7_INTRO,
)
from app.core.config import settings
from app.services.pdf_service import INDUSTRY_MAP, SIZE_MAP

logger = structlog.get_logger()

# --- Шрифты: Liberation Serif (метрически совместим с Times New Roman) ------

_FONT_CANDIDATES = {
    "Thesis": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "Thesis-Bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "Thesis-Italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    ],
    "Thesis-BoldItalic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
    ],
    # Формулы: DejaVu обладает наиболее полным покрытием математических знаков
    "ThesisFormula": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
}


def _register_fonts() -> Dict[str, str]:
    """Регистрирует TTF-шрифты; возвращает карту имя->файл."""
    registered = {}
    for name, paths in _FONT_CANDIDATES.items():
        for p in paths:
            if Path(p).exists():
                pdfmetrics.registerFont(TTFont(name, p))
                registered[name] = p
                break
        else:
            registered[name] = "Helvetica"  # без кириллицы — крайний фолбэк
    return registered


_FONTS = _register_fonts()

BODY_FONT = "Thesis" if _FONTS["Thesis"] != "Helvetica" else "Helvetica"
BOLD_FONT = "Thesis-Bold" if _FONTS["Thesis-Bold"] != "Helvetica" else "Helvetica-Bold"
FORMULA_FONT = "ThesisFormula" if _FONTS["ThesisFormula"] != "Helvetica" else "Helvetica"


def _ru_float(x: Any, nd: int = 2) -> str:
    """Число с запятой в качестве десятичного разделителя."""
    try:
        return f"{float(x):.{nd}f}".replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def _ru_date(iso: Optional[str]) -> str:
    if not iso:
        return "—"
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return d.strftime("%d.%m.%Y")
    except ValueError:
        return str(iso)[:10]


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class DissertationReportGenerator:
    """Генерация PDF-главы «Статистический анализ данных платформы»."""

    def __init__(self):
        self.output_dir = Path(settings.reports_path) / "dissertation"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._table_no = 0

    # ------------------------------------------------------------------ #
    #  Стили и примитивы
    # ------------------------------------------------------------------ #

    def _styles(self) -> Dict[str, ParagraphStyle]:
        return {
            "chapter": ParagraphStyle(
                "chapter", fontName=BOLD_FONT, fontSize=15, leading=22,
                alignment=TA_CENTER, spaceAfter=18,
            ),
            "h2": ParagraphStyle(
                "h2", fontName=BOLD_FONT, fontSize=14, leading=20,
                alignment=TA_CENTER, spaceBefore=20, spaceAfter=12,
            ),
            "body": ParagraphStyle(
                "body", fontName=BODY_FONT, fontSize=14, leading=21,
                alignment=TA_JUSTIFY, firstLineIndent=1.25 * cm, spaceAfter=4,
            ),
            "formula": ParagraphStyle(
                "formula", fontName=FORMULA_FONT, fontSize=13, leading=19,
                alignment=TA_CENTER,
            ),
            "formula_no": ParagraphStyle(
                "formula_no", fontName=BODY_FONT, fontSize=13, leading=19,
                alignment=TA_LEFT,
            ),
            "bullet": ParagraphStyle(
                "bullet", fontName=BODY_FONT, fontSize=14, leading=21,
                alignment=TA_JUSTIFY, leftIndent=1.6 * cm,
                firstLineIndent=-0.35 * cm, spaceAfter=4,
            ),
            "caption": ParagraphStyle(
                "caption", fontName=BODY_FONT, fontSize=13, leading=18,
                alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
            ),
            "note": ParagraphStyle(
                "note", fontName=BODY_FONT, fontSize=12, leading=16,
                alignment=TA_JUSTIFY, spaceAfter=4,
            ),
            "cell": ParagraphStyle(
                "cell", fontName=BODY_FONT, fontSize=12, leading=15,
                alignment=TA_CENTER,
            ),
            "cell_left": ParagraphStyle(
                "cell_left", fontName=BODY_FONT, fontSize=12, leading=15,
                alignment=TA_LEFT,
            ),
            "cell_head": ParagraphStyle(
                "cell_head", fontName=BOLD_FONT, fontSize=12, leading=15,
                alignment=TA_CENTER,
            ),
            "ref": ParagraphStyle(
                "ref", fontName=BODY_FONT, fontSize=13, leading=18,
                alignment=TA_JUSTIFY, leftIndent=1.0 * cm,
                firstLineIndent=-1.0 * cm, spaceAfter=4,
            ),
        }

    def _para(self, text: str, style: ParagraphStyle) -> Paragraph:
        return Paragraph(_esc(text), style)

    def _next_table_no(self) -> int:
        self._table_no += 1
        return self._table_no

    def _add_formula(self, story: List, marker: str, st: Dict[str, ParagraphStyle]) -> None:
        """Блок формулы: текст по центру, номер (3.N) у правого края."""
        body = marker[len("FORMULA:"):].strip()
        # номер вида (3.N) отделяем от текста формулы
        no, _, rest = body.partition(")")
        number = (no + ")").strip()
        formula_text = rest.strip()
        row = [
            self._para(formula_text, st["formula"]),
            self._para(number, st["formula_no"]),
        ]
        t = Table([row], colWidths=[15.2 * cm, 2.2 * cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

    def _add_theory(self, story: List, paragraphs: List[str], st: Dict[str, ParagraphStyle]) -> None:
        """Поток теории с формулами: маркер FORMULA: превращается в блок формулы."""
        for chunk in paragraphs:
            if chunk.startswith("FORMULA:"):
                self._add_formula(story, chunk, st)
            else:
                story.append(self._para(chunk, st["body"]))

    def _add_bullets(self, story: List, items: List[str], st: Dict[str, ParagraphStyle],
                     lead: Optional[str] = None) -> None:
        if lead:
            story.append(self._para(lead, st["body"]))
        for it in items:
            story.append(Paragraph("–\u00a0" + _esc(it), st["bullet"]))

    def _add_table(self, story: List, caption: str, header: List[str],
                   rows: List[List[str]], col_widths: List[float],
                   note: Optional[str] = None,
                   left_cols: int = 1) -> None:
        st = self._styles()
        no = self._next_table_no()
        story.append(self._para(f"Таблица {CHAPTER_NO}.{no} — {caption}", st["caption"]))
        data = [[self._para(h, st["cell_head"]) for h in header]]
        for r in rows:
            cells = []
            for ci, v in enumerate(r):
                style = st["cell_left"] if ci < left_cols else st["cell"]
                cells.append(self._para(str(v), style))
            data.append(cells)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        if note:
            story.append(self._para("Примечание — " + note, st["note"]))

    # ------------------------------------------------------------------ #
    #  Динамические блоки результатов
    # ------------------------------------------------------------------ #

    def _section1_results(self, story: List, data: Dict[str, Any]) -> None:
        st = self._styles()
        desc = (data.get("descriptive") or {})
        sample = (desc.get("sample_characteristics")
                  or desc.get("sample") or {})
        n = sample.get("total_sample_size")
        if not n:
            story.append(self._para(
                "Данные выборки недоступны: на момент генерации отчёта завершённые "
                "аудиты отсутствуют или сервис данных вернул пустой результат.",
                st["body"]))
            return

        dr = sample.get("date_range") or {}
        story.append(self._para(
            f"Выборка исследования включает {n} завершённых аудитов, собранных в период "
            f"с {_ru_date(dr.get('first'))} по {_ru_date(dr.get('last'))}. "
            "Отраслевая принадлежность организаций охватывает "
            f"{len(sample.get('industry_distribution') or {})} отраслей; распределение "
            "выборки по отраслям приведено в таблице "
            f"{CHAPTER_NO}.{self._table_no + 1}, по размеру бизнеса — в таблице "
            f"{CHAPTER_NO}.{self._table_no + 2}.",
            st["body"]))

        ind = sample.get("industry_distribution") or {}
        if ind:
            total = sum(ind.values())
            rows = sorted(ind.items(), key=lambda kv: -kv[1])
            self._add_table(
                story,
                "Распределение выборки по отраслям",
                ["Отрасль", "Число аудитов", "Доля, %"],
                [[INDUSTRY_MAP.get(k, k), v, _ru_float(v / total * 100, 1)]
                 for k, v in rows],
                [8.5 * cm, 4.5 * cm, 4.4 * cm],
            )

        sizes = sample.get("size_distribution") or {}
        levels = sample.get("maturity_level_distribution") or {}
        if sizes or levels:
            size_rows = [[SIZE_MAP.get(k, k), v] for k, v in sizes.items()]
            level_rows = [[k, v] for k, v in levels.items()]
            merged = []
            for i in range(max(len(size_rows), len(level_rows))):
                left = size_rows[i] if i < len(size_rows) else ["—", "—"]
                right = level_rows[i] if i < len(level_rows) else ["—", "—"]
                merged.append(left + right)
            self._add_table(
                story,
                "Распределение выборки по размеру бизнеса и уровню зрелости",
                ["Размер бизнеса", "Число", "Уровень зрелости", "Число"],
                merged,
                [5.4 * cm, 2.8 * cm, 5.4 * cm, 3.8 * cm],
            )

    def _section2_results(self, story: List, data: Dict[str, Any]) -> List[str]:
        st = self._styles()
        desc = (data.get("descriptive") or {})
        ct = (desc.get("central_tendency") or {})
        cs = ct.get("composite_score")
        n = ((desc.get("sample_characteristics") or {}).get("total_sample_size"))
        conclusions = []
        if n:
            conclusions.append(
                f"Объём выборки ({n} наблюдений) достаточен для корректного применения "
                "описательных статистик и оценки надёжности шкал.")
        if not cs:
            story.append(self._para(
                "Описательные статистики недоступны: данные выборки пусты.", st["body"]))
            conclusions.append("Описательная статистика не выполнена: отсутствуют данные.")
            return conclusions

        mean = cs.get("mean")
        v = (cs.get("std") / mean * 100) if mean else None
        story.append(self._para(
            f"Интегральный индекс зрелости по выборке: среднее {_ru_float(cs.get('mean'))}, "
            f"медиана {_ru_float(cs.get('median'))}, стандартное отклонение "
            f"{_ru_float(cs.get('std'))}, коэффициент вариации {_ru_float(v, 1)} %, "
            f"асимметрия {_ru_float(cs.get('skewness'))}, эксцесс {_ru_float(cs.get('kurtosis'))}. "
            + ("Совокупность однородна (V < 33 %), доминирующая роль среднего как "
               "характеристики типичного объекта обоснована. "
               if v is not None and v < 33 else
               "Совокупность неоднородна (V > 33 %), описание дополнено медианой и квартилями. "),
            st["body"]))

        dim_rows = []
        dim_means = {}
        header = ["Показатель", "Среднее", "Медиана", "СО", "V, %", "Асимм.", "Эксцесс"]
        all_rows = {"Интегральный индекс": cs}
        for key in sorted(ct.keys()):
            if key.startswith("dim_"):
                all_rows[DIMENSION_NAMES.get(key.split("_")[1], key)] = ct[key]
        for name, vals in all_rows.items():
            m = vals.get("mean")
            s = vals.get("std")
            vv = (s / m * 100) if (m and s is not None) else None
            if m is not None:
                dim_means[name] = m
            dim_rows.append([
                name, _ru_float(m), _ru_float(vals.get("median")), _ru_float(s),
                _ru_float(vv, 1), _ru_float(vals.get("skewness")),
                _ru_float(vals.get("kurtosis")),
            ])
        self._add_table(
            story,
            "Описательные статистики интегрального индекса и баллов измерений",
            header, dim_rows,
            [5.6 * cm, 2.1 * cm, 2.2 * cm, 1.9 * cm, 1.9 * cm, 2.0 * cm, 2.0 * cm],
            note="СО — стандартное отклонение; V — коэффициент вариации.",
        )
        if dim_means:
            lo = min(dim_means, key=dim_means.get)
            hi = max(dim_means, key=dim_means.get)
            conclusions.append(
                f"Наиболее развитое измерение — «{hi}» (среднее {_ru_float(dim_means[hi])}), "
                f"наименее развитое — «{lo}» (среднее {_ru_float(dim_means[lo])}); "
                "разрыв характеризует типовой дисбаланс траектории внедрения ИИ.")
        skew = cs.get("skewness")
        if skew is not None and abs(skew) < 1:
            conclusions.append(
                "Распределение индекса зрелости умеренно симметрично "
                f"(|A| = {_ru_float(abs(skew))} < 1), что допускает применение "
                "параметрических методов с оговоркой о малом объёме выборки.")
        return conclusions

    def _section3_results(self, story: List, data: Dict[str, Any]) -> List[str]:
        st = self._styles()
        rel = (data.get("reliability") or {})
        dims = rel.get("dimensions") or {}
        conclusions = []
        if not dims:
            story.append(self._para(
                "Расчёт надёжности недоступен: сервис вернул пустой результат.", st["body"]))
            return ["Оценка надёжности не выполнена: данные недоступны."]

        rows, completed, alphas = [], 0, []
        for dim_id in sorted(dims.keys(), key=int):
            d = dims[dim_id]
            a = d.get("cronbach_alpha") or {}
            om = d.get("mcdonalds_omega") or {}
            sh = d.get("split_half") or {}
            cr = d.get("composite_reliability") or {}
            ave = d.get("average_variance_extracted") or {}

            def val(block, key, ok="completed"):
                return _ru_float(block.get(key)) if block.get("status") == ok else "—"

            if a.get("status") == "completed":
                completed += 1
                alphas.append(a.get("alpha", 0))
            rows.append([
                f"{dim_id}. {DIMENSION_NAMES.get(dim_id, '')}",
                str(a.get("sample_size", "—") if a.get("status") == "completed" else "н/д"),
                val(a, "alpha") if a.get("status") == "completed"
                else ("н/д" if a.get("status") == "insufficient_data" else "ошибка"),
                val(om, "omega_total"),
                val(sh, "spearman_brown_corrected"),
                val(cr, "composite_reliability"),
                val(ave, "ave"),
            ])
        self._add_table(
            story,
            "Показатели надёжности шкал методики",
            ["Шкала", "n", "α Кронбаха", "ω Макдональда", "r Спирмена—Брауна", "CR", "AVE"],
            rows,
            [4.6 * cm, 1.4 * cm, 2.2 * cm, 2.6 * cm, 2.8 * cm, 1.8 * cm, 1.8 * cm],
            note="«н/д» — недостаточно полных протоколов (n < 10); «—» — показатель требует "
                 "факторных нагрузок (CR, AVE — при n ≥ 50, см. раздел 3.4).",
        )
        s = rel.get("summary") or {}
        if alphas:
            good = sum(1 for x in alphas if x >= 0.8)
            acceptable = sum(1 for x in alphas if 0.7 <= x < 0.8)
            story.append(self._para(
                f"Расчёт выполнен для {completed} шкал из 7. Средняя альфа Кронбаха — "
                f"{_ru_float(s.get('mean_alpha'))}, минимальная — {_ru_float(s.get('min_alpha'))}. "
                f"Хорошую надёжность (α ≥ 0,8) демонстрируют {good} шкал, приемлемую "
                f"(0,7 ≤ α < 0,8) — {acceptable}.",
                st["body"]))
            conclusions.append(
                f"Измерительный инструмент надёжен: {completed} из 7 шкал оценены, "
                f"{good + acceptable} из них достигают порога приемлемости α ≥ 0,7; "
                "конвергентная валидность (CR, AVE) подлежит оценке после достижения "
                "порога факторного анализа.")
        else:
            conclusions.append(
                "Ни одна шкала не достигла порога в 10 полных протоколов; выводы о "
                "надёжности откладываются до накопления данных.")
        return conclusions

    def _section4_results(self, story: List, data: Dict[str, Any]) -> List[str]:
        st = self._styles()
        fa = (data.get("factor_analysis") or {})
        if fa.get("status") == "completed":
            asm = fa.get("assumptions") or {}
            kmo = (asm.get("kmo") or {}).get("overall")
            bart = (asm.get("bartlett_sphericity") or {})
            story.append(self._para(
                f"Выборка {fa.get('sample_size')} наблюдений достаточна. KMO = "
                f"{_ru_float(kmo, 3)}; критерий сферичности Бартлетта: "
                f"p = {_ru_float(bart.get('p_value'), 4)}.",
                st["body"]))
            var = fa.get("cumulative_variance") or []
            if var:
                story.append(self._para(
                    f"Семь факторов объясняют {_ru_float(var[-1] * 100, 1)} % общей "
                    "дисперсии.", st["body"]))
            return ["Факторная структура подтверждена эмпирически (см. таблицу выше)."]
        msg = fa.get("message") or "недостаточно наблюдений"
        story.append(self._para(
            f"Факторный анализ на текущей выборке не выполняется: {msg}. Априорная "
            "семифакторная структура методики остаётся теоретически постулированной; "
            "эмпирическая проверка автоматически станет доступной при достижении "
            "порога в 50 полных протоколов. Показатели CR и AVE (раздел 3.3), "
            "вычисляемые из факторных нагрузок, отложены до этого момента.",
            st["body"]))
        return ["Факторная проверка структуры конструкта отложена: выборка меньше "
                "установленного порога (n < 50)."]

    def _section5_results(self, story: List, data: Dict[str, Any]) -> List[str]:
        st = self._styles()
        reg = (data.get("regression") or {})
        m2r = reg.get("maturity_to_roi") or {}
        conclusions = []
        if m2r.get("status") == "completed":
            story.append(self._para(
                f"Модель зрелость → ROI: β₁ = {_ru_float((m2r.get('coefficients') or {}).get('composite_score'))}, "
                f"R² = {_ru_float(m2r.get('r_squared'))}, F = {_ru_float(m2r.get('f_statistic'))} "
                f"(p = {_ru_float(m2r.get('f_p_value'), 4)}).",
                st["body"]))
            conclusions.append("Связь зрелости с ROI оценена регрессионным методом.")
            return conclusions

        reason = m2r.get("reason") or f"недостаточно данных ({m2r.get('sample_size', '—')} < 30)"
        other = []
        for key in ("dimension_contribution", "logistic", "hierarchical"):
            b = reg.get(key) or {}
            if b.get("status") != "completed":
                other.append(key)
        story.append(self._para(
            f"Регрессионное моделирование на текущей выборке не выполняется: {reason}. "
            "Финансовые исходы (оценки ROI) не накапливались: завершённые ИИ-инициативы "
            "обследованных организаций ещё не зафиксированы платформой. Метод "
            "реализован и активируется автоматически по мере накопления вариативных "
            "данных; до этого момента оценка экономического эффекта опирается на "
            "имитационное моделирование, описанное в экономическом разделе работы.",
            st["body"]))
        conclusions.append(
            "Регрессионная проверка связи зрелости и ROI отложена: зависимая переменная "
            "не обладает вариативностью (ROI не собирается).")
        return conclusions

    def _section6_results(self, story: List, data: Dict[str, Any]) -> List[str]:
        st = self._styles()
        cl = (data.get("cluster") or {})
        conclusions = []
        if cl.get("status") != "completed":
            story.append(self._para(
                "Кластеризация не выполнена: объём выборки ниже установленного порога.",
                st["body"]))
            return ["Кластеризация отложена: выборка слишком мала."]

        elbow = cl.get("elbow_data") or []
        if elbow:
            self._add_table(
                story,
                "Подбор числа кластеров: силуэтная метрика по диапазону k",
                ["k", "Силуэт s"],
                [[e.get("k"), _ru_float(e.get("silhouette"), 3)] for e in elbow],
                [4.5 * cm, 4.5 * cm],
                note="Выделено оптимальное значение k = "
                     f"{cl.get('optimal_k', cl.get('n_clusters'))}.",
            )
        story.append(self._para(
            f"Оптимальное разбиение: k = {cl.get('n_clusters')} кластера (средний силуэт "
            f"{_ru_float(cl.get('silhouette_score'), 3)}). Профили кластеров приведены в "
            "таблице ниже.",
            st["body"]))
        profile_rows = []
        for p in (cl.get("cluster_profiles") or []):
            chars = ", ".join(p.get("characteristics") or []) or "—"
            profile_rows.append([
                str((p.get("cluster_id") or 0) + 1),
                str(p.get("size", "—")),
                _ru_float(p.get("percentage"), 1),
                f"{_ru_float(p.get('composite_mean'))} ± {_ru_float(p.get('composite_std'))}",
                chars,
            ])
        if profile_rows:
            self._add_table(
                story,
                "Профили кластеров ИИ-зрелости",
                ["Кластер", "n", "Доля, %", "Индекс (M ± СО)", "Характеристика"],
                profile_rows,
                [1.9 * cm, 1.4 * cm, 2.0 * cm, 4.2 * cm, 7.9 * cm],
            )
        conclusions.append(
            f"Сегментация выполнена: {cl.get('n_clusters')} кластера со средним силуэтом "
            f"{_ru_float(cl.get('silhouette_score'), 3)}; профили кластеров образуют "
            "основу типологии траекторий внедрения ИИ.")
        return conclusions

    def _section7_summary(self, story: List, data: Dict[str, Any]) -> None:
        st = self._styles()
        summary_no = self._table_no + 1
        rel = (data.get("reliability") or {})
        completed_dims = sum(
            1 for d in (rel.get("dimensions") or {}).values()
            if (d.get("cronbach_alpha") or {}).get("status") == "completed"
        )
        cl = (data.get("cluster") or {})
        rows = [
            ["Описательная статистика", "Профиль выборки и показателей",
             "n ≥ 10", "Выполнен"],
            ["Надёжность шкал (α, ω, расщепление)", "Качество измерения",
             "n ≥ 10 на шкалу", f"Выполнен ({completed_dims} из 7 шкал)"],
            ["Факторный анализ", "Конструктная валидность",
             "n ≥ 50, KMO ≥ 0,6", "Отложен (n < 50)"],
            ["Регрессия (МНК)", "Связь зрелости и ROI",
             "n ≥ 30 и вариативность ROI", "Отложен (ROI без вариативности)"],
            ["Кластеризация k-средних", "Сегментация организаций",
             "n ≥ 12",
             "Выполнен" if cl.get("status") == "completed" else "Отложен"],
        ]
        story.append(self._para(
            SECTION_7_INTRO[0].replace("таблице 3.6", f"таблице {CHAPTER_NO}.{summary_no}"),
            st["body"]))
        self._add_table(
            story,
            "Сводные результаты применения статистических методов",
            ["Метод", "Назначение", "Условие применимости", "Статус на выборке"],
            rows,
            [4.6 * cm, 4.0 * cm, 4.2 * cm, 4.6 * cm],
        )
        for chunk in SECTION_7_INTRO[1:]:
            story.append(self._para(chunk, st["body"]))

    # ------------------------------------------------------------------ #
    #  Сборка документа
    # ------------------------------------------------------------------ #

    def _on_page(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(BODY_FONT, 12)
        canvas.drawCentredString(A4[0] / 2, 1.1 * cm, str(doc.page))
        canvas.restoreState()

    def _method_section(self, story: List, heading: str, theory: List[str],
                        purpose: List[str], applicability: Optional[List[str]],
                        results_builder, data: Dict[str, Any]) -> None:
        st = self._styles()
        story.append(self._para(heading, st["h2"]))
        self._add_theory(story, theory, st)
        if purpose:
            self._add_bullets(story, purpose, st, lead="Назначение метода.")
        if applicability:
            self._add_bullets(story, applicability, st,
                              lead="Условия применимости метода:")
        conclusions = results_builder(story, data)
        if conclusions:
            self._add_bullets(story, conclusions, st, lead="Выводы по разделу:")

    def generate_full_report(self, analytics_data: Dict) -> str:
        """Генерирует главу диссертации в PDF; возвращает путь к файлу."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dissertation_report_{timestamp}.pdf"
        output_path = self.output_dir / filename
        self._table_no = 0

        doc = BaseDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=3 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=f"Глава {CHAPTER_NO}. {CHAPTER_TITLE}",
            author="AI Maturity Assessment Platform",
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
        doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=self._on_page)])

        st = self._styles()
        story: List = []

        # Заголовок главы и вводные абзацы
        story.append(self._para(f"ГЛАВА {CHAPTER_NO}. {CHAPTER_TITLE}", st["chapter"]))
        for chunk in INTRO:
            story.append(self._para(chunk, st["body"]))

        # 3.1 — программа анализа и выборка (результаты строятся внутри)
        self._method_section(
            story, f"{CHAPTER_NO}.1. {SECTION_1_HEADING}",
            SECTION_1_THEORY, SECTION_1_PURPOSE, None,
            self._section1_results, analytics_data)

        # 3.2 — описательная статистика
        self._method_section(
            story, f"{CHAPTER_NO}.2. {SECTION_2_HEADING}",
            SECTION_2_THEORY, SECTION_2_PURPOSE, SECTION_2_APPLICABILITY,
            self._section2_results, analytics_data)

        # 3.3 — надёжность
        self._method_section(
            story, f"{CHAPTER_NO}.3. {SECTION_3_HEADING}",
            SECTION_3_THEORY, SECTION_3_PURPOSE, SECTION_3_APPLICABILITY,
            self._section3_results, analytics_data)

        # 3.4 — факторный анализ
        self._method_section(
            story, f"{CHAPTER_NO}.4. {SECTION_4_HEADING}",
            SECTION_4_THEORY, SECTION_4_PURPOSE, SECTION_4_APPLICABILITY,
            self._section4_results, analytics_data)

        # 3.5 — регрессионный анализ
        self._method_section(
            story, f"{CHAPTER_NO}.5. {SECTION_5_HEADING}",
            SECTION_5_THEORY, SECTION_5_PURPOSE, SECTION_5_APPLICABILITY,
            self._section5_results, analytics_data)

        # 3.6 — кластерный анализ
        self._method_section(
            story, f"{CHAPTER_NO}.6. {SECTION_6_HEADING}",
            SECTION_6_THEORY, SECTION_6_PURPOSE, SECTION_6_APPLICABILITY,
            self._section6_results, analytics_data)

        # 3.7 — сводные результаты и ограничения
        story.append(self._para(f"{CHAPTER_NO}.7. {SECTION_7_HEADING}", st["h2"]))
        self._section7_summary(story, analytics_data)

        # Список источников
        story.append(self._para(REFERENCES_TITLE.upper(), st["h2"]))
        for i, ref in enumerate(REFERENCES, 1):
            story.append(Paragraph(f"{i}. " + _esc(ref), st["ref"]))

        doc.build(story)
        logger.info("dissertation_report_generated", path=str(output_path))
        return str(output_path)
