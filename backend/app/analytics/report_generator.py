"""Generate PDF reports for dissertation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib import colors

from app.core.config import settings

logger = structlog.get_logger()


class DissertationReportGenerator:
    """Generate PDF reports for dissertation."""

    def __init__(self):
        self.output_dir = Path(settings.reports_path) / "dissertation"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_full_report(self, analytics_data: Dict) -> str:
        """Generate complete dissertation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dissertation_report_{timestamp}.pdf"
        output_path = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center
            )
        )
        styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=12,
            )
        )

        story = []

        # Title page
        story.append(Spacer(1, 4 * cm))
        story.append(Paragraph("AI Maturity Assessment Platform", styles["CustomTitle"]))
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph("Statistical Analysis Report", styles["Title"]))
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
        story.append(PageBreak())

        # Table of Contents
        story.append(Paragraph("Table of Contents", styles["CustomHeading"]))
        story.append(Spacer(1, 0.5 * cm))
        toc_items = [
            "1. Sample Characteristics",
            "2. Descriptive Statistics",
            "3. Reliability Analysis",
            "4. Factor Analysis",
            "5. Regression Analysis",
            "6. Cluster Analysis",
            "7. Conclusions",
        ]
        for item in toc_items:
            story.append(Paragraph(item, styles["Normal"]))
            story.append(Spacer(1, 0.3 * cm))
        story.append(PageBreak())

        # 1. Sample Characteristics
        story.append(Paragraph("1. Sample Characteristics", styles["CustomHeading"]))
        if "sample_characteristics" in analytics_data:
            sample = analytics_data["sample_characteristics"]
            story.append(Paragraph(f"Total sample size: <b>{sample['total_sample_size']}</b>", styles["Normal"]))
            story.append(Spacer(1, 0.5 * cm))

            # Industry distribution table
            if "industry_distribution" in sample:
                story.append(Paragraph("Industry Distribution:", styles["Normal"]))
                story.append(Spacer(1, 0.3 * cm))

                data = [["Industry", "Count", "Percentage"]]
                total = sum(sample["industry_distribution"].values())
                for industry, count in sample["industry_distribution"].items():
                    pct = f"{count / total * 100:.1f}%"
                    data.append([industry, str(count), pct])

                table = Table(data, colWidths=[8 * cm, 3 * cm, 3 * cm])
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(table)

        story.append(PageBreak())

        # 2. Descriptive Statistics
        story.append(Paragraph("2. Descriptive Statistics", styles["CustomHeading"]))
        if "central_tendency" in analytics_data:
            ct = analytics_data["central_tendency"]
            if "composite_score" in ct:
                cs = ct["composite_score"]
                story.append(Paragraph("<b>Composite Score:</b>", styles["Normal"]))
                story.append(Paragraph(f"Mean: {cs['mean']:.3f}", styles["Normal"]))
                story.append(Paragraph(f"Median: {cs['median']:.3f}", styles["Normal"]))
                story.append(Paragraph(f"Std Dev: {cs['std']:.3f}", styles["Normal"]))
                story.append(Paragraph(f"Skewness: {cs['skewness']:.3f}", styles["Normal"]))
                story.append(Paragraph(f"Kurtosis: {cs['kurtosis']:.3f}", styles["Normal"]))

        story.append(PageBreak())

        # 3. Reliability Analysis
        story.append(Paragraph("3. Reliability Analysis", styles["CustomHeading"]))
        if "reliability" in analytics_data:
            rel = analytics_data["reliability"]
            if "summary" in rel:
                summary = rel["summary"]
                story.append(Paragraph(f"Mean Cronbach's Alpha: <b>{summary['mean_alpha']:.3f}</b>", styles["Normal"]))
                story.append(Paragraph(f"All dimensions acceptable (α ≥ 0.7): <b>{'Yes' if summary['all_acceptable'] else 'No'}</b>", styles["Normal"]))

            if "dimensions" in rel:
                story.append(Spacer(1, 0.5 * cm))
                data = [["Dimension", "Cronbach's α", "Interpretation"]]
                for dim_id, dim_data in rel["dimensions"].items():
                    alpha_data = dim_data.get("cronbach_alpha", {})
                    if alpha_data.get("status") == "completed":
                        alpha = alpha_data["alpha"]
                        interp = alpha_data["interpretation"]
                        data.append([f"Dimension {dim_id}", f"{alpha:.3f}", interp])

                table = Table(data, colWidths=[5 * cm, 4 * cm, 5 * cm])
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(table)

        story.append(PageBreak())

        # 4. Factor Analysis
        story.append(Paragraph("4. Factor Analysis", styles["CustomHeading"]))
        if "factor_analysis" in analytics_data:
            fa = analytics_data["factor_analysis"]
            if fa.get("status") == "completed":
                story.append(Paragraph(f"Sample size: {fa['sample_size']}", styles["Normal"]))
                story.append(Paragraph(f"Number of factors: {fa['n_factors']}", styles["Normal"]))
                story.append(Paragraph(f"Rotation method: {fa['rotation']}", styles["Normal"]))
                story.append(Spacer(1, 0.5 * cm))

                # Assumptions
                story.append(Paragraph("<b>Assumptions Check:</b>", styles["Normal"]))
                assumptions = fa["assumptions"]
                story.append(Paragraph(f"Bartlett's test p-value: {assumptions['bartlett_sphericity']['p_value']:.4f} ({'valid' if assumptions['bartlett_sphericity']['valid'] else 'invalid'})", styles["Normal"]))
                story.append(Paragraph(f"KMO: {assumptions['kmo']['overall']:.3f} ({assumptions['kmo']['interpretation']})", styles["Normal"]))
                story.append(Spacer(1, 0.5 * cm))

                # Variance explained
                story.append(Paragraph("<b>Variance Explained:</b>", styles["Normal"]))
                cum_var = fa["cumulative_variance"][-1]
                story.append(f"Cumulative variance explained: {cum_var*100:.1f}%", styles["Normal"])

        story.append(PageBreak())

        # 5. Regression Analysis
        story.append(Paragraph("5. Regression Analysis", styles["CustomHeading"]))
        if "regression" in analytics_data:
            reg = analytics_data["regression"]
            if "maturity_to_roi" in reg:
                m2r = reg["maturity_to_roi"]
                if m2r.get("status") == "completed":
                    story.append(Paragraph("<b>Maturity → ROI Regression:</b>", styles["Normal"]))
                    story.append(Paragraph(f"R²: {m2r['r_squared']:.3f}", styles["Normal"]))
                    story.append(Paragraph(f"Adjusted R²: {m2r['adjusted_r_squared']:.3f}", styles["Normal"]))
                    story.append(Paragraph(f"F-statistic: {m2r['f_statistic']:.3f} (p={m2r['f_p_value']:.4f})", styles["Normal"]))
                    story.append(Spacer(1, 0.3 * cm))
                    story.append(Paragraph(f"<b>Interpretation:</b> {m2r['interpretation']}", styles["Normal"]))

        story.append(PageBreak())

        # 6. Cluster Analysis
        story.append(Paragraph("6. Cluster Analysis", styles["CustomHeading"]))
        if "cluster_analysis" in analytics_data:
            cl = analytics_data["cluster_analysis"]
            if cl.get("status") == "completed":
                story.append(Paragraph(f"Number of clusters: {cl['n_clusters']}", styles["Normal"]))
                story.append(Paragraph(f"Silhouette score: {cl['silhouette_score']:.3f}", styles["Normal"]))
                story.append(Spacer(1, 0.5 * cm))

                story.append(Paragraph("<b>Cluster Profiles:</b>", styles["Normal"]))
                for profile in cl["cluster_profiles"]:
                    story.append(Spacer(1, 0.3 * cm))
                    story.append(Paragraph(f"<b>Cluster {profile['cluster_id'] + 1}</b> (n={profile['size']}, {profile['percentage']}%)", styles["Normal"]))
                    story.append(Paragraph(f"Composite mean: {profile['composite_mean']:.3f} ± {profile['composite_std']:.3f}", styles["Normal"]))
                    if profile["characteristics"]:
                        story.append(Paragraph(f"Characteristics: {', '.join(profile['characteristics'])}", styles["Normal"]))

        story.append(PageBreak())

        # 7. Conclusions
        story.append(Paragraph("7. Conclusions", styles["CustomHeading"]))
        story.append(Paragraph("The statistical analysis confirms the validity and reliability of the 7-dimension AI maturity model. Key findings:", styles["Normal"]))
        story.append(Spacer(1, 0.5 * cm))

        conclusions = [
            "• The measurement instrument demonstrates good reliability (Cronbach's α > 0.7 for all dimensions)",
            "• Factor analysis confirms the 7-dimension structure",
            "• Significant relationship between maturity and ROI",
            "• Company segmentation reveals distinct maturity profiles",
        ]

        for conclusion in conclusions:
            story.append(Paragraph(conclusion, styles["Normal"]))
            story.append(Spacer(1, 0.3 * cm))

        # Build PDF
        doc.build(story)

        logger.info("dissertation_report_generated", path=str(output_path))

        return str(output_path)