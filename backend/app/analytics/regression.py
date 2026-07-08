"""Regression analysis — maturity to ROI, financial outcomes."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import structlog

from app.storage.json_storage import JSONStorage

logger = structlog.get_logger()


class RegressionService:
    """Service for regression analysis."""

    def __init__(self):
        self.storage = JSONStorage()

    def _prepare_dataset(self) -> pd.DataFrame:
        """Prepare dataset for regression."""
        audits = self.storage.list_audits(limit=100000)
        active = [a for a in audits if a.get("status") != "archived"]

        rows = []
        for audit in active:
            indices = audit.get("calculated_indices", {})
            profile = audit.get("company_profile", {})
            financial = audit.get("financial_outcomes", {})

            row = {
                "audit_id": audit.get("audit_id"),
                "composite_score": indices.get("composite_score", 0),
                "maturity_level": indices.get("maturity_level", ""),
                "roi_percent": indices.get("roi_estimate_percent", 0),
                "tco_millions": indices.get("tco_estimate_millions", 0),
                "industry": profile.get("industry", ""),
                "company_size": profile.get("company_size", ""),
                "region": profile.get("region", ""),
                "ai_experience_years": profile.get("ai_experience_years", 0),
                "it_budget_millions": profile.get("annual_it_budget_millions", 0),
            }

            # Add dimension scores
            for dim_id, score in indices.get("dimension_scores", {}).items():
                row[f"dim_{dim_id}"] = score

            # Add financial outcomes if available
            row["actual_roi"] = financial.get("actual_roi_percent")
            row["actual_revenue_growth"] = financial.get("revenue_growth_percent")

            rows.append(row)

        return pd.DataFrame(rows)

    def maturity_to_roi_regression(self) -> Dict[str, Any]:
        """Linear regression: maturity score → ROI."""
        df = self._prepare_dataset()

        if len(df) < 30:
            return {"status": "insufficient_data", "sample_size": len(df)}

        # Simple linear regression
        X = sm.add_constant(df["composite_score"])
        y = df["roi_percent"]

        model = sm.OLS(y, X).fit()

        # Check assumptions
        residuals = model.resid
        shapiro_stat, shapiro_p = stats.shapiro(residuals[:500])  # Shapiro-Wilk

        # Heteroscedasticity (Breusch-Pagan)
        from statsmodels.stats.diagnostic import het_breuschpagan

        bp_test = het_breuschpagan(residuals, X)

        return {
            "status": "completed",
            "sample_size": len(df),
            "model_type": "OLS",
            "dependent": "ROI (%)",
            "independent": "Composite Maturity Score",
            "coefficients": {
                "intercept": {
                    "value": float(model.params[0]),
                    "p_value": float(model.pvalues[0]),
                    "ci_95": [float(model.conf_int().iloc[0, 0]), float(model.conf_int().iloc[0, 1])],
                },
                "composite_score": {
                    "value": float(model.params[1]),
                    "p_value": float(model.pvalues[1]),
                    "ci_95": [float(model.conf_int().iloc[1, 0]), float(model.conf_int().iloc[1, 1])],
                },
            },
            "r_squared": float(model.rsquared),
            "adjusted_r_squared": float(model.rsquared_adj),
            "f_statistic": float(model.fvalue),
            "f_p_value": float(model.f_pvalue),
            "assumptions": {
                "normality": {
                    "shapiro_w": float(shapiro_stat),
                    "shapiro_p": float(shapiro_p),
                    "valid": shapiro_p > 0.05,
                },
                "heteroscedasticity": {
                    "breusch_pagan_lm": float(bp_test[0]),
                    "breusch_pagan_p": float(bp_test[1]),
                    "valid": bp_test[1] > 0.05,
                },
            },
            "interpretation": self._interpret_regression(model),
        }

    def dimension_contribution_regression(self) -> Dict[str, Any]:
        """Multiple regression: all dimensions → ROI."""
        df = self._prepare_dataset()

        if len(df) < 50:
            return {"status": "insufficient_data", "sample_size": len(df)}

        # Prepare features
        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        X = sm.add_constant(df[dim_cols])
        y = df["roi_percent"]

        model = sm.OLS(y, X).fit()

        # Standardized coefficients
        X_std = (df[dim_cols] - df[dim_cols].mean()) / df[dim_cols].std()
        y_std = (y - y.mean()) / y.std()
        model_std = sm.OLS(y_std, sm.add_constant(X_std)).fit()

        # VIF (Variance Inflation Factor)
        from statsmodels.stats.outliers_influence import variance_inflation_factor

        vif = pd.DataFrame()
        vif["feature"] = dim_cols
        vif["VIF"] = [
            variance_inflation_factor(X.values, i + 1) for i in range(len(dim_cols))
        ]

        return {
            "status": "completed",
            "sample_size": len(df),
            "model_type": "Multiple OLS",
            "r_squared": float(model.rsquared),
            "adjusted_r_squared": float(model.rsquared_adj),
            "f_statistic": float(model.fvalue),
            "f_p_value": float(model.f_pvalue),
            "coefficients": {
                col: {
                    "value": float(model.params[col]),
                    "std_value": float(model_std.params[col]),
                    "p_value": float(model.pvalues[col]),
                    "ci_95": [
                        float(model.conf_int().loc[col, 0]),
                        float(model.conf_int().loc[col, 1]),
                    ],
                }
                for col in dim_cols
            },
            "vif": vif.to_dict(orient="records"),
            "multicollinearity_check": all(vif["VIF"] < 10),
            "most_predictive_dimension": max(
                dim_cols, key=lambda c: abs(model_std.params[c])
            ),
        }

    def logistic_regression_maturity_level(self) -> Dict[str, Any]:
        """Logistic regression: predict high maturity (L4-L5) from dimensions."""
        df = self._prepare_dataset()

        if len(df) < 50:
            return {"status": "insufficient_data"}

        # Binary target: L4 or L5 = 1, else 0
        df["high_maturity"] = df["maturity_level"].apply(
            lambda x: 1 if "L4" in x or "L5" in x else 0
        )

        dim_cols = [f"dim_{i}" for i in range(1, 8)]
        X = sm.add_constant(df[dim_cols])
        y = df["high_maturity"]

        model = sm.Logit(y, X).fit(disp=0)

        # Odds ratios
        odds_ratios = np.exp(model.params)

        return {
            "status": "completed",
            "sample_size": len(df),
            "positive_cases": int(y.sum()),
            "negative_cases": int(len(y) - y.sum()),
            "pseudo_r_squared": float(model.prsquared),
            "aic": float(model.aic),
            "bic": float(model.bic),
            "coefficients": {
                col: {
                    "value": float(model.params[col]),
                    "odds_ratio": float(odds_ratios[col]),
                    "p_value": float(model.pvalues[col]),
                    "ci_95": [
                        float(model.conf_int().loc[col, 0]),
                        float(model.conf_int().loc[col, 1]),
                    ],
                }
                for col in dim_cols
            },
            "classification_accuracy": float((model.predict(X) > 0.5).mean()),
        }

    def hierarchical_regression(self) -> Dict[str, Any]:
        """Hierarchical regression: control variables → dimensions → outcome."""
        df = self._prepare_dataset()

        if len(df) < 50:
            return {"status": "insufficient_data"}

        # Control variables
        controls = ["ai_experience_years", "it_budget_millions"]
        dim_cols = [f"dim_{i}" for i in range(1, 8)]

        # Step 1: Controls only
        X1 = sm.add_constant(df[controls])
        y = df["roi_percent"]
        model1 = sm.OLS(y, X1).fit()

        # Step 2: Controls + dimensions
        X2 = sm.add_constant(df[controls + dim_cols])
        model2 = sm.OLS(y, X2).fit()

        # R-squared change
        r2_change = model2.rsquared - model1.rsquared

        # F-test for change
        from scipy.stats import f as f_dist

        df_change = len(dim_cols)
        df_residual = len(df) - len(controls) - len(dim_cols) - 1
        f_change = (r2_change / df_change) / ((1 - model2.rsquared) / df_residual)
        p_change = 1 - f_dist.cdf(f_change, df_change, df_residual)

        return {
            "status": "completed",
            "sample_size": len(df),
            "step1": {
                "predictors": controls,
                "r_squared": float(model1.rsquared),
                "f_statistic": float(model1.fvalue),
                "f_p_value": float(model1.f_pvalue),
            },
            "step2": {
                "predictors": controls + dim_cols,
                "r_squared": float(model2.rsquared),
                "adjusted_r_squared": float(model2.rsquared_adj),
                "f_statistic": float(model2.fvalue),
                "f_p_value": float(model2.f_pvalue),
            },
            "model_comparison": {
                "r_squared_change": float(r2_change),
                "f_change": float(f_change),
                "p_change": float(p_change),
                "significant": p_change < 0.05,
            },
        }

    def moderation_analysis(self, moderator: str = "company_size") -> Dict[str, Any]:
        """Moderation analysis: does company size moderate maturity-ROI relationship?"""
        df = self._prepare_dataset()

        if len(df) < 50:
            return {"status": "insufficient_data"}

        # Create interaction term
        df["maturity_x_moderator"] = df["composite_score"] * df[moderator]

        X = sm.add_constant(df[["composite_score", moderator, "maturity_x_moderator"]])
        y = df["roi_percent"]

        model = sm.OLS(y, X).fit()

        return {
            "status": "completed",
            "sample_size": len(df),
            "moderator": moderator,
            "r_squared": float(model.rsquared),
            "coefficients": {
                "main_effect_maturity": {
                    "value": float(model.params["composite_score"]),
                    "p_value": float(model.pvalues["composite_score"]),
                },
                "main_effect_moderator": {
                    "value": float(model.params[moderator]),
                    "p_value": float(model.pvalues[moderator]),
                },
                "interaction": {
                    "value": float(model.params["maturity_x_moderator"]),
                    "p_value": float(model.pvalues["maturity_x_moderator"]),
                    "significant": model.pvalues["maturity_x_moderator"] < 0.05,
                },
            },
            "interpretation": "Moderation effect detected"
            if model.pvalues["maturity_x_moderator"] < 0.05
            else "No moderation effect",
        }

    def _interpret_regression(self, model) -> str:
        """Generate plain-language interpretation."""
        r2 = model.rsquared
        coef = model.params[1]

        interpretation = f"The model explains {r2*100:.1f}% of variance in ROI. "
        interpretation += f"For each 1-point increase in maturity score, "
        interpretation += f"ROI increases by {coef:.1f} percentage points."

        if model.pvalues[1] < 0.001:
            interpretation += " This effect is highly significant (p < 0.001)."
        elif model.pvalues[1] < 0.01:
            interpretation += " This effect is significant (p < 0.01)."
        elif model.pvalues[1] < 0.05:
            interpretation += " This effect is significant (p < 0.05)."
        else:
            interpretation += " This effect is not statistically significant."

        return interpretation