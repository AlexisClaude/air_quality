"""End-to-end workflow assembling the base Air Quality pipeline."""

from dataclasses import dataclass, field

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import RFE
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.pipeline import Pipeline

from air_quality import data, evaluation, features, transformers

DEFAULT_COLUMNS = [
    "city",
    "date",
    "hour",
    "site_latitude",
    "site_longitude",
    "pm2_5",
    "sulphurdioxide_so2_column_number_density",
    "carbonmonoxide_co_column_number_density",
    "nitrogendioxide_no2_column_number_density",
    "formaldehyde_tropospheric_hcho_column_number_density",
    "uvaerosolindex_absorbing_aerosol_index",
    "ozone_o3_column_number_density",
    "uvaerosollayerheight_aerosol_height",
    "cloud_cloud_fraction",
]


@dataclass
class PipelineConfig:
    """Settings for run_baseline: which cities, which columns, how much data."""

    train_city: str = "Kampala"
    test_city: str = "Nairobi"
    columns: list[str] = field(default_factory=lambda: list(DEFAULT_COLUMNS))
    max_rows_per_city: int = 1200
    random_state: int = 42


def run_baseline(config: PipelineConfig | None = None) -> dict[str, float]:
    """
    Load, clean, split by city, engineer features, train and evaluate a linear baseline.

    Parameters:
    - config: pipeline settings; a default PipelineConfig() is used if omitted

    Returns:
    - dict of regression metrics (see evaluation.regression_metrics)
    """
    config = config or PipelineConfig()
    train_df, _ = data.load_datasets()
    cities = [config.train_city, config.test_city]

    scoped = data.restrict_to_scope(
        train_df, cities, config.columns, config.max_rows_per_city, config.random_state
    )
    fillable_columns = [c for c in config.columns if c not in ("city", "date")]
    cleaned = data.fill_missing_by_city(scoped, fillable_columns)
    enriched = features.add_temporal_features(cleaned)

    train_split = enriched[enriched["city"] == config.train_city]
    test_split = enriched[enriched["city"] == config.test_city]

    feature_cols = features.feature_columns(enriched)
    model = LinearRegression()
    return evaluation.evaluate_manual_split(model, train_split, test_split, feature_cols)


# ============================================================================
# Session 3 — optional modules (not needed for Session 2's practical_3)
# ============================================================================


@dataclass
class AdvancedPipelineConfig:
    """
    Settings for run_advanced. Starts with what Module 2 needs; later modules may
    add or remove fields here as your pipeline evolves — see each module's page
    under content/session3/ for what changes.
    """

    train_city: str = "Kampala"
    test_city: str = "Bujumbura"
    cities: list[str] = field(
        default_factory=lambda: ["Kampala", "Nairobi", "Lagos", "Bujumbura"]
    )
    columns: list[str] | None = None
    missing_threshold: float = 0.6
    n_features_to_select: int = 8


def run_advanced(config: AdvancedPipelineConfig | None = None) -> dict:
    """
    The Session 3 pipeline: starts where run_baseline stops, and grows one optional
    module at a time. Each module you complete under content/session3/ tells you
    exactly what to add or change here — this function is yours to write and
    maintain, not something given to you complete.

    There is deliberately no automated test for it: its correct shape depends on
    which optional modules you have added, something no fixed test could know in
    advance. Verify it by running scripts/run_pipeline.py and checking that the
    printed metrics make sense for whatever you have built so far.

    Parameters:
    - config: pipeline settings; a default AdvancedPipelineConfig() is used if omitted

    Returns:
    - dict of metrics — the exact shape depends on which modules you have added
    """
    config = config or AdvancedPipelineConfig()
    train_df, _ = data.load_datasets()

    excluded_columns = {"id", "site_id", "country", "month"}
    columns = config.columns or [
        column for column in train_df.columns if column not in excluded_columns
    ]
    scoped = data.restrict_to_scope(
        train_df,
        config.cities,
        columns,
    )
    enriched = features.add_temporal_features(scoped)
    X = enriched.drop(columns="pm2_5")
    y = enriched["pm2_5"]
    groups = enriched["city"]

    pipeline = Pipeline(
        steps=[
            (
                "cleaner",
                transformers.AirQualityCleaner(
                    missing_threshold=config.missing_threshold
                ),
            ),
            (
                "selector",
                RFE(
                    estimator=LinearRegression(),
                    n_features_to_select=config.n_features_to_select,
                ),
            ),
            ("model", LinearRegression()),
        ]
    )
    splitter = GroupKFold(n_splits=groups.nunique())
    cv_results = cross_validate(
        pipeline,
        X,
        y,
        groups=groups,
        cv=splitter,
        scoring={
            "rmse": "neg_root_mean_squared_error",
            "mae": "neg_mean_absolute_error",
            "r2": "r2",
        },
        error_score="raise",
    )
    test_groups = [
        groups.iloc[test_idx].iloc[0]
        for _, test_idx in splitter.split(X, y, groups)
    ]
    metric_scores = {
        "rmse": -cv_results["test_rmse"],
        "mae": -cv_results["test_mae"],
        "r2": cv_results["test_r2"],
    }
    results = {
        "folds": [
            {
                "test_group": test_group,
                **{
                    metric: float(scores[index])
                    for metric, scores in metric_scores.items()
                },
            }
            for index, test_group in enumerate(test_groups)
        ]
    }
    for metric, scores in metric_scores.items():
        results[f"{metric}_mean"] = float(np.mean(scores))
        results[f"{metric}_std"] = float(np.std(scores))
    return results
