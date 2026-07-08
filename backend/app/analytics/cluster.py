"""Cluster analysis — segmentation of companies by maturity profile."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import structlog
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class ClusterAnalysisService:
    """Service for cluster analysis of companies."""

    def __init__(self):
        self.storage = JSONStorage()

    def _prepare_dataset(self) -> pd.DataFrame:
        """Prepare dataset for clustering."""
        audits = self.storage.list_audits(limit=100000)
        active = [a for a in audits if a.get("status") != "archived"]

        rows = []
        for audit in active:
            indices = audit.get("calculated_indices", {})
            profile = audit.get("company_profile", {})

            row = {
                "audit_id": audit.get("audit_id"),
                "industry": profile.get("industry", ""),
                "company_size": profile.get("company_size", ""),
                "region": profile.get("region", ""),
            }

            for dim_id, score in indices.get("dimension_scores", {}).items():
                row[f"dim_{dim_id}"] = score

            row["composite_score"] = indices.get("composite_score", 0)

            rows.append(row)

        return pd.DataFrame(rows)

    def kmeans_clustering(
        self, n_clusters: int = 4, max_k: int = 10
    ) -> Dict[str, Any]:
        """K-means clustering with optimal k selection."""
        df = self._prepare_dataset()

        if len(df) < 30:
            return {"status": "insufficient_data", "sample_size": len(df)}

        # Prepare features
        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        X = df[dim_cols].values

        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Find optimal k using silhouette score
        silhouette_scores = []
        inertias = []

        for k in range(2, min(max_k + 1, len(df) // 2)):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            silhouette_scores.append(silhouette_score(X_scaled, labels))
            inertias.append(kmeans.inertia_)

        optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2

        # Final clustering with optimal k or specified k
        final_k = n_clusters if n_clusters != 4 else optimal_k
        kmeans = KMeans(n_clusters=final_k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        # Add labels to dataframe
        df["cluster"] = labels

        # Cluster profiles
        cluster_profiles = self._compute_cluster_profiles(df, dim_cols)

        # Elbow data
        elbow_data = [
            {"k": k, "inertia": inertias[k - 2], "silhouette": silhouette_scores[k - 2]}
            for k in range(2, max_k + 1)
        ]

        return {
            "status": "completed",
            "sample_size": len(df),
            "n_clusters": final_k,
            "optimal_k": optimal_k,
            "silhouette_score": float(silhouette_score(X_scaled, labels)),
            "cluster_sizes": df["cluster"].value_counts().to_dict(),
            "cluster_profiles": cluster_profiles,
            "elbow_data": elbow_data,
            "cluster_centers": kmeans.cluster_centers_.tolist(),
        }

    def hierarchical_clustering(self, n_clusters: int = 4) -> Dict[str, Any]:
        """Hierarchical (agglomerative) clustering."""
        df = self._prepare_dataset()

        if len(df) < 30:
            return {"status": "insufficient_data"}

        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        X = df[dim_cols].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Hierarchical clustering
        Z = linkage(X_scaled, method="ward")
        labels = fcluster(Z, n_clusters, criterion="maxclust")

        df["cluster"] = labels - 1  # 0-indexed

        cluster_profiles = self._compute_cluster_profiles(df, dim_cols)

        return {
            "status": "completed",
            "sample_size": len(df),
            "n_clusters": n_clusters,
            "linkage_method": "ward",
            "cluster_sizes": df["cluster"].value_counts().to_dict(),
            "cluster_profiles": cluster_profiles,
        }

    def _compute_cluster_profiles(
        self, df: pd.DataFrame, dim_cols: List[str]
    ) -> List[Dict[str, Any]]:
        """Compute profile for each cluster."""
        profiles = []

        for cluster_id in sorted(df["cluster"].unique()):
            cluster_df = df[df["cluster"] == cluster_id]

            profile = {
                "cluster_id": int(cluster_id),
                "size": len(cluster_df),
                "percentage": round(len(cluster_df) / len(df) * 100, 1),
                "dimension_means": {
                    col: float(cluster_df[col].mean()) for col in dim_cols
                },
                "composite_mean": float(cluster_df["composite_score"].mean()),
                "composite_std": float(cluster_df["composite_score"].std()),
                "industry_distribution": cluster_df["industry"].value_counts().to_dict(),
                "size_distribution": cluster_df["company_size"].value_counts().to_dict(),
            }

            # Identify cluster characteristics
            profile["characteristics"] = self._identify_characteristics(profile)

            profiles.append(profile)

        return profiles

    def _identify_characteristics(self, profile: Dict) -> List[str]:
        """Identify key characteristics of a cluster."""
        characteristics = []

        dim_means = profile["dimension_means"]
        avg_dim = sum(dim_means.values()) / len(dim_means)

        # Find strongest and weakest dimensions
        max_dim = max(dim_means, key=dim_means.get)
        min_dim = min(dim_means, key=dim_means.get)

        dimension_names = {
            "dim_1": "Strategy",
            "dim_2": "Data",
            "dim_3": "Technology",
            "dim_4": "Processes",
            "dim_5": "People",
            "dim_6": "Culture",
            "dim_7": "Ethics",
        }

        if dim_means[max_dim] > avg_dim + 0.5:
            characteristics.append(
                f"Strong in {dimension_names.get(max_dim, max_dim)}"
            )

        if dim_means[min_dim] < avg_dim - 0.5:
            characteristics.append(
                f"Weak in {dimension_names.get(min_dim, min_dim)}"
            )

        # Overall maturity level
        composite = profile["composite_mean"]
        if composite >= 4.0:
            characteristics.append("High maturity")
        elif composite >= 3.0:
            characteristics.append("Medium maturity")
        else:
            characteristics.append("Low maturity")

        return characteristics

    def compare_industries(self) -> Dict[str, Any]:
        """Compare maturity profiles across industries."""
        df = self._prepare_dataset()

        industry_stats = []
        for industry, group in df.groupby("industry"):
            if len(group) < 5:
                continue

            stats_dict = {
                "industry": industry,
                "sample_size": len(group),
                "composite_mean": float(group["composite_score"].mean()),
                "composite_std": float(group["composite_score"].std()),
                "composite_median": float(group["composite_score"].median()),
            }

            for i in range(1, 8):
                col = f"dim_{i}"
                stats_dict[f"dim_{i}_mean"] = float(group[col].mean())

            industry_stats.append(stats_dict)

        # ANOVA test
        from scipy.stats import f_oneway

        groups = [
            group["composite_score"].values
            for _, group in df.groupby("industry")
            if len(group) >= 5
        ]

        if len(groups) >= 2:
            f_stat, p_value = f_oneway(*groups)
        else:
            f_stat, p_value = 0, 1

        return {
            "status": "completed",
            "n_industries": len(industry_stats),
            "industry_statistics": industry_stats,
            "anova": {
                "f_statistic": float(f_stat),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
            },
        }