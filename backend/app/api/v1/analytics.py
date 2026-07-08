"""Analytics API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from app.analytics.cluster import ClusterAnalysisService
from app.analytics.descriptive import DescriptiveStatisticsService
from app.analytics.factor_analysis import FactorAnalysisService
from app.analytics.regression import RegressionService
from app.analytics.reliability import ReliabilityService
from app.analytics.unified_service import UnifiedAnalyticsService
from app.core.deps import AuthUser, require_analyst, require_facilitator

router = APIRouter()


# ──────────────────────────────────────────────────
# DESCRIPTIVE STATISTICS
# ──────────────────────────────────────────────────


@router.get("/descriptive/sample")
async def get_sample_characteristics(user: AuthUser = Depends(require_analyst)):
    """Get sample characteristics."""
    service = DescriptiveStatisticsService()
    return service.sample_characteristics()


@router.get("/descriptive/central-tendency")
async def get_central_tendency(user: AuthUser = Depends(require_analyst)):
    """Get measures of central tendency."""
    service = DescriptiveStatisticsService()
    return service.central_tendency()


@router.get("/descriptive/distribution")
async def get_distribution_analysis(user: AuthUser = Depends(require_analyst)):
    """Get distribution analysis."""
    service = DescriptiveStatisticsService()
    return service.distribution_analysis()


@router.get("/descriptive/correlation")
async def get_correlation_analysis(user: AuthUser = Depends(require_analyst)):
    """Get correlation matrix."""
    service = DescriptiveStatisticsService()
    return service.correlation_analysis()


@router.get("/descriptive/outliers")
async def get_outliers_analysis(user: AuthUser = Depends(require_analyst)):
    """Get outliers analysis."""
    service = DescriptiveStatisticsService()
    return service.outliers_analysis()


@router.get("/descriptive/full")
async def get_full_descriptive(user: AuthUser = Depends(require_analyst)):
    """Get complete descriptive statistics."""
    service = DescriptiveStatisticsService()
    return service.full_descriptive_report()


# ──────────────────────────────────────────────────
# RELIABILITY
# ──────────────────────────────────────────────────


@router.get("/reliability/dimension/{dimension_id}")
async def get_dimension_reliability(
    dimension_id: int, user: AuthUser = Depends(require_analyst)
):
    """Get reliability metrics for a dimension."""
    service = ReliabilityService()
    return {
        "cronbach_alpha": service.cronbach_alpha(dimension_id),
        "mcdonalds_omega": service.mcdonalds_omega(dimension_id),
        "split_half": service.split_half_reliability(dimension_id),
        "composite_reliability": service.composite_reliability(dimension_id),
        "average_variance_extracted": service.average_variance_extracted(dimension_id),
    }


@router.get("/reliability/full")
async def get_full_reliability(user: AuthUser = Depends(require_analyst)):
    """Get complete reliability report."""
    service = ReliabilityService()
    return service.full_reliability_report()


# ──────────────────────────────────────────────────
# FACTOR ANALYSIS
# ──────────────────────────────────────────────────


@router.get("/factor-analysis/efa")
async def run_efa(
    n_factors: int = Query(7, ge=1, le=15),
    method: str = Query("minres"),
    rotation: str = Query("promax"),
    user: AuthUser = Depends(require_analyst),
):
    """Run Exploratory Factor Analysis."""
    service = FactorAnalysisService()
    return service.run_efa(n_factors=n_factors, method=method, rotation=rotation)


@router.get("/factor-analysis/pca")
async def run_pca(
    n_components: int = Query(7, ge=1, le=15),
    user: AuthUser = Depends(require_analyst),
):
    """Run Principal Component Analysis."""
    service = FactorAnalysisService()
    return service.run_pca(n_components=n_components)


@router.get("/factor-analysis/optimal-factors")
async def determine_optimal_factors(
    max_factors: int = Query(10, ge=2, le=15),
    user: AuthUser = Depends(require_analyst),
):
    """Determine optimal number of factors."""
    service = FactorAnalysisService()
    return service.determine_optimal_factors(max_factors=max_factors)


# ──────────────────────────────────────────────────
# REGRESSION
# ──────────────────────────────────────────────────


@router.get("/regression/maturity-to-roi")
async def maturity_to_roi_regression(user: AuthUser = Depends(require_analyst)):
    """Regression: maturity → ROI."""
    service = RegressionService()
    return service.maturity_to_roi_regression()


@router.get("/regression/dimension-contribution")
async def dimension_contribution(user: AuthUser = Depends(require_analyst)):
    """Multiple regression: dimensions → ROI."""
    service = RegressionService()
    return service.dimension_contribution_regression()


@router.get("/regression/logistic")
async def logistic_regression(user: AuthUser = Depends(require_analyst)):
    """Logistic regression: predict high maturity."""
    service = RegressionService()
    return service.logistic_regression_maturity_level()


@router.get("/regression/hierarchical")
async def hierarchical_regression(user: AuthUser = Depends(require_analyst)):
    """Hierarchical regression."""
    service = RegressionService()
    return service.hierarchical_regression()


@router.get("/regression/moderation")
async def moderation_analysis(
    moderator: str = Query("company_size"),
    user: AuthUser = Depends(require_analyst),
):
    """Moderation analysis."""
    service = RegressionService()
    return service.moderation_analysis(moderator=moderator)


# ──────────────────────────────────────────────────
# CLUSTER ANALYSIS
# ──────────────────────────────────────────────────


@router.get("/cluster/kmeans")
async def kmeans_clustering(
    n_clusters: int = Query(4, ge=2, le=10),
    user: AuthUser = Depends(require_analyst),
):
    """K-means clustering."""
    service = ClusterAnalysisService()
    return service.kmeans_clustering(n_clusters=n_clusters)


@router.get("/cluster/hierarchical")
async def hierarchical_clustering(
    n_clusters: int = Query(4, ge=2, le=10),
    user: AuthUser = Depends(require_analyst),
):
    """Hierarchical clustering."""
    service = ClusterAnalysisService()
    return service.hierarchical_clustering(n_clusters=n_clusters)


@router.get("/cluster/industry-comparison")
async def industry_comparison(user: AuthUser = Depends(require_analyst)):
    """Compare industries."""
    service = ClusterAnalysisService()
    return service.compare_industries()


# ──────────────────────────────────────────────────
# FULL ANALYSIS & REPORTS
# ──────────────────────────────────────────────────


@router.post("/full-analysis")
async def run_full_analysis(user: AuthUser = Depends(require_facilitator)):
    """Run complete analytics pipeline."""
    service = UnifiedAnalyticsService()
    return service.run_full_analysis()


@router.post("/generate-report")
async def generate_dissertation_report(user: AuthUser = Depends(require_facilitator)):
    """Generate dissertation PDF report."""
    service = UnifiedAnalyticsService()
    report_path = service.generate_dissertation_report()
    return {"report_path": report_path, "status": "completed"}


@router.post("/export")
async def export_for_dissertation(
    format: str = Query("all", pattern="^(all|json|csv|pdf)$"),
    user: AuthUser = Depends(require_facilitator),
):
    """Export all results for dissertation."""
    service = UnifiedAnalyticsService()
    return service.export_for_dissertation(format=format)


@router.get("/download-report/{filename}")
async def download_report(filename: str, user: AuthUser = Depends(require_analyst)):
    """Download generated report."""
    from pathlib import Path

    from app.core.config import settings

    report_path = Path(settings.reports_path) / "dissertation" / filename

    if not report_path.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=str(report_path),
        filename=filename,
        media_type="application/pdf",
    )