"""Unified analytics service — orchestrates all analyses."""

from typing import Any, Dict

import structlog

from app.analytics.cluster import ClusterAnalysisService
from app.analytics.descriptive import DescriptiveStatisticsService
from app.analytics.factor_analysis import FactorAnalysisService
from app.analytics.regression import RegressionService
from app.analytics.reliability import ReliabilityService
from app.analytics.report_generator import DissertationReportGenerator
from app.analytics.visualization import VisualizationService

logger = structlog.get_logger()


class UnifiedAnalyticsService:
    """Orchestrates all analytics for dissertation."""

    def __init__(self):
        self.factor = FactorAnalysisService()
        self.reliability = ReliabilityService()
        self.regression = RegressionService()
        self.cluster = ClusterAnalysisService()
        self.descriptive = DescriptiveStatisticsService()
        self.visualization = VisualizationService()
        self.report = DissertationReportGenerator()

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analytics pipeline."""
        logger.info("full_analysis_started")

        results = {}

        # 1. Descriptive statistics
        logger.info("running_descriptive_statistics")
        results["descriptive"] = self.descriptive.full_descriptive_report()

        # 2. Reliability analysis
        logger.info("running_reliability_analysis")
        results["reliability"] = self.reliability.full_reliability_report()

        # 3. Factor analysis
        logger.info("running_factor_analysis")
        results["factor_analysis"] = self.factor.run_efa(n_factors=7)

        # 4. PCA (for comparison)
        logger.info("running_pca")
        results["pca"] = self.factor.run_pca(n_components=7)

        # 5. Optimal factors
        logger.info("determining_optimal_factors")
        results["optimal_factors"] = self.factor.determine_optimal_factors()

        # 6. Regression analysis
        logger.info("running_regression_analysis")
        results["regression"] = {
            "maturity_to_roi": self.regression.maturity_to_roi_regression(),
            "dimension_contribution": self.regression.dimension_contribution_regression(),
            "logistic": self.regression.logistic_regression_maturity_level(),
            "hierarchical": self.regression.hierarchical_regression(),
        }

        # 7. Cluster analysis
        logger.info("running_cluster_analysis")
        results["cluster_analysis"] = self.cluster.kmeans_clustering()

        # 8. Industry comparison
        logger.info("running_industry_comparison")
        results["industry_comparison"] = self.cluster.compare_industries()

        # 9. Generate visualizations
        logger.info("generating_visualizations")
        results["figures"] = self.visualization.generate_all_figures(results)

        logger.info("full_analysis_completed")

        return results

    def generate_dissertation_report(self) -> str:
        """Generate complete dissertation PDF report."""
        # Run analysis
        analytics_data = self.run_full_analysis()

        # Generate PDF
        report_path = self.report.generate_full_report(analytics_data)

        return report_path

    def export_for_dissertation(self, format: str = "all") -> Dict[str, str]:
        """Export all results in dissertation-ready formats."""
        import json
        from pathlib import Path

        from app.core.config import settings

        export_dir = Path(settings.exports_path) / "dissertation"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Run analysis
        results = self.run_full_analysis()

        exports = {}

        # JSON export
        if format in ["all", "json"]:
            json_path = export_dir / "analytics_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            exports["json"] = str(json_path)

        # CSV exports
        if format in ["all", "csv"]:
            import pandas as pd

            # Correlation matrix
            if "descriptive" in results and "correlation_analysis" in results["descriptive"]:
                corr_df = pd.DataFrame(results["descriptive"]["correlation_analysis"]["correlation_matrix"])
                corr_path = export_dir / "correlation_matrix.csv"
                corr_df.to_csv(corr_path)
                exports["correlation_csv"] = str(corr_path)

            # Factor loadings
            if "factor_analysis" in results and results["factor_analysis"].get("status") == "completed":
                loadings_df = pd.DataFrame(results["factor_analysis"]["loadings"]).T
                loadings_path = export_dir / "factor_loadings.csv"
                loadings_df.to_csv(loadings_path)
                exports["loadings_csv"] = str(loadings_path)

        # PDF report
        if format in ["all", "pdf"]:
            pdf_path = self.generate_dissertation_report()
            exports["pdf"] = pdf_path

        return exports