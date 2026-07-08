"""Scientific visualizations for dissertation."""

import io
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Scientific style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


class VisualizationService:
    """Service for generating scientific visualizations."""

    def __init__(self):
        self.output_dir = Path(settings.reports_path) / "figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def correlation_heatmap(self, corr_matrix: Dict, filename: str = "correlation_heatmap.png") -> str:
        """Generate correlation heatmap."""
        df = pd.DataFrame(corr_matrix)

        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(df, dtype=bool))

        sns.heatmap(
            df,
            mask=mask,
            cmap="coolwarm",
            annot=True,
            fmt=".2f",
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
        )

        plt.title("Correlation Matrix Between Dimensions", fontsize=14, pad=20)
        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def scree_plot(self, eigenvalues: list, filename: str = "scree_plot.png") -> str:
        """Generate scree plot for factor analysis."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Eigenvalues
        ax.plot(
            range(1, len(eigenvalues) + 1),
            eigenvalues,
            "bo-",
            linewidth=2,
            markersize=8,
            label="Eigenvalues",
        )

        # Eigenvalue = 1 line
        ax.axhline(y=1, color="r", linestyle="--", label="Eigenvalue = 1")

        ax.set_xlabel("Factor Number", fontsize=12)
        ax.set_ylabel("Eigenvalue", fontsize=12)
        ax.set_title("Scree Plot", fontsize=14, pad=20)
        ax.legend()
        ax.set_xticks(range(1, len(eigenvalues) + 1))
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def factor_loadings_plot(self, loadings: Dict, filename: str = "factor_loadings.png") -> str:
        """Generate factor loadings plot."""
        df = pd.DataFrame(loadings).T

        fig, ax = plt.subplots(figsize=(12, 8))

        # Heatmap of loadings
        sns.heatmap(
            df,
            cmap="RdBu_r",
            center=0,
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            ax=ax,
            cbar_kws={"label": "Factor Loading"},
        )

        plt.title("Factor Loadings Matrix", fontsize=14, pad=20)
        plt.xlabel("Factors", fontsize=12)
        plt.ylabel("Items", fontsize=12)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def maturity_distribution(self, scores: list, filename: str = "maturity_distribution.png") -> str:
        """Generate maturity score distribution plot."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Histogram with KDE
        sns.histplot(scores, bins=20, kde=True, ax=ax, color="steelblue")

        # Add mean and median lines
        mean = np.mean(scores)
        median = np.median(scores)

        ax.axvline(mean, color="red", linestyle="--", label=f"Mean = {mean:.2f}")
        ax.axvline(median, color="green", linestyle="--", label=f"Median = {median:.2f}")

        ax.set_xlabel("Composite Maturity Score", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title("Distribution of AI Maturity Scores", fontsize=14, pad=20)
        ax.legend()

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def regression_plot(self, x: list, y: list, model_summary: Dict, filename: str = "regression_plot.png") -> str:
        """Generate regression scatter plot with fit line."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Scatter plot
        ax.scatter(x, y, alpha=0.6, s=50, color="steelblue", edgecolors="white")

        # Regression line
        x_array = np.array(x)
        y_pred = model_summary["coefficients"]["intercept"]["value"] + \
                 model_summary["coefficients"]["composite_score"]["value"] * x_array

        ax.plot(x_array, y_pred, "r-", linewidth=2, label="Regression line")

        # Add R² and equation
        r2 = model_summary["r_squared"]
        coef = model_summary["coefficients"]["composite_score"]["value"]
        intercept = model_summary["coefficients"]["intercept"]["value"]

        equation = f"y = {intercept:.2f} + {coef:.2f}x\nR² = {r2:.3f}"
        ax.text(
            0.05, 0.95, equation,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        ax.set_xlabel("Composite Maturity Score", fontsize=12)
        ax.set_ylabel("ROI (%)", fontsize=12)
        ax.set_title("Relationship Between Maturity and ROI", fontsize=14, pad=20)
        ax.legend()

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def cluster_plot(self, cluster_data: Dict, filename: str = "cluster_plot.png") -> str:
        """Generate cluster visualization (PCA-reduced)."""
        from sklearn.decomposition import PCA

        centers = np.array(cluster_data["cluster_centers"])

        # PCA for 2D visualization
        pca = PCA(n_components=2)
        centers_2d = pca.fit_transform(centers)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot cluster centers
        colors = plt.cm.Set1(np.linspace(0, 1, len(centers)))

        for i, (center, color) in enumerate(zip(centers_2d, colors)):
            size = cluster_data["cluster_sizes"].get(i, 0)
            ax.scatter(
                center[0], center[1],
                s=size * 10,
                c=[color],
                label=f"Cluster {i+1} (n={size})",
                alpha=0.7,
                edgecolors="black",
                linewidth=2,
            )

        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=12)
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=12)
        ax.set_title("Cluster Visualization (PCA-reduced)", fontsize=14, pad=20)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def boxplot_by_industry(self, data: Dict, filename: str = "industry_boxplot.png") -> str:
        """Generate boxplot of maturity scores by industry."""
        fig, ax = plt.subplots(figsize=(12, 6))

        industries = [d["industry"] for d in data]
        means = [d["composite_mean"] for d in data]
        stds = [d["composite_std"] for d in data]

        # Sort by mean
        sorted_idx = np.argsort(means)[::-1]
        industries = [industries[i] for i in sorted_idx]
        means = [means[i] for i in sorted_idx]
        stds = [stds[i] for i in sorted_idx]

        y_pos = np.arange(len(industries))

        ax.barh(y_pos, means, xerr=stds, align="center", alpha=0.7, color="steelblue")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(industries)
        ax.set_xlabel("Composite Maturity Score", fontsize=12)
        ax.set_title("AI Maturity by Industry", fontsize=14, pad=20)
        ax.invert_yaxis()

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def radar_chart_dimensions(self, dimension_means: Dict, filename: str = "radar_dimensions.png") -> str:
        """Generate radar chart of dimension scores."""
        dimension_names = {
            "dim_1": "Strategy",
            "dim_2": "Data",
            "dim_3": "Technology",
            "dim_4": "Processes",
            "dim_5": "People",
            "dim_6": "Culture",
            "dim_7": "Ethics",
        }

        labels = [dimension_names.get(k, k) for k in dimension_means.keys()]
        values = list(dimension_means.values())

        # Number of variables
        N = len(labels)

        # Compute angles
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        values += values[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        ax.plot(angles, values, "b-", linewidth=2)
        ax.fill(angles, values, "b", alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8)
        ax.set_title("Average Dimension Scores", fontsize=14, pad=20)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def generate_all_figures(self, analytics_results: Dict) -> Dict[str, str]:
        """Generate all figures for dissertation."""
        figures = {}

        try:
            # Correlation heatmap
            if "correlation_analysis" in analytics_results:
                figures["correlation"] = self.correlation_heatmap(
                    analytics_results["correlation_analysis"]["correlation_matrix"]
                )

            # Scree plot
            if "factor_analysis" in analytics_results:
                figures["scree"] = self.scree_plot(
                    analytics_results["factor_analysis"]["eigenvalues"]
                )

                figures["loadings"] = self.factor_loadings_plot(
                    analytics_results["factor_analysis"]["loadings"]
                )

            # Maturity distribution
            if "distribution_analysis" in analytics_results:
                # Need raw scores - would fetch from storage
                pass

            logger.info("figures_generated", count=len(figures))

        except Exception as e:
            logger.error("figure_generation_failed", error=str(e))

        return figures