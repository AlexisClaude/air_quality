"""Compare feature selectors across the Module 5 XGBoost grid in MLflow."""

import sys
from pathlib import Path

from sklearn.linear_model import LinearRegression

# Make the src-layout package importable when run from a checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from air_quality import data, features, selection, tracking, tuning

ALL_CITIES = ["Kampala", "Nairobi", "Lagos", "Bujumbura"]
EXCLUDED_RAW_COLUMNS = {"id", "site_id", "country", "month"}


def main() -> None:
    """
    Rebuild the cleaned dataset, compare SelectKBest and RFE, and log each
    feature-selector/hyperparameter combination as its own MLflow run.
    """
    # TODO: reuse the Module 2/4/5 functions you already completed —
    # restrict_to_scope (scope to ALL_CITIES and every column except
    # EXCLUDED_RAW_COLUMNS), columns_above_missing_threshold + drop_columns
    # (threshold 0.7), fill_missing_by_city, add_temporal_features,
    # feature_columns, then select_features_rfe (n_features_to_select=8) to
    # get back the same 8 columns as Module 5. Run tune_xgboost with
    # param_grid={"max_depth": [3, 5], "learning_rate": [0.05, 0.2]}, then
    # loop over tuning_result["cv_results"] and call tracking.log_run once
    # per grid point — a short run_name built from combo["params"],
    # params=combo["params"], and metrics={"rmse": combo["rmse"],
    # "mae": combo["mae"], "r2": combo["r2"]} — before printing a short
    # confirmation once every combination has been logged
    # (implementation follows below)

    missing_threshold = 0.7
    train_df, _ = data.load_datasets()
    columns = [
        column for column in train_df.columns
        if column not in EXCLUDED_RAW_COLUMNS
    ]
    scoped = data.restrict_to_scope(train_df, ALL_CITIES, columns)

    columns_to_drop = data.columns_above_missing_threshold(
        scoped, threshold=missing_threshold
    )
    cleaned = data.drop_columns(scoped, columns_to_drop)
    fillable_columns = [
        column for column in cleaned.columns if column not in ("city", "date")
    ]
    cleaned = data.fill_missing_by_city(cleaned, fillable_columns)
    enriched = features.add_temporal_features(cleaned)

    feature_cols = features.feature_columns(enriched)
    param_grid = {"max_depth": [3, 5], "learning_rate": [0.05, 0.2]}
    logged_runs = []
    feature_sets = {
        "select_k_best": selection.select_k_best_features(
            enriched,
            feature_cols,
            target_col="pm2_5",
            k=8,
        ),
        "rfe": selection.select_features_rfe(
            model=LinearRegression(),
            df=enriched,
            feature_cols=feature_cols,
            target_col="pm2_5",
            n_features_to_select=8,
        ),
    }

    for selector_name, selected_features in feature_sets.items():
        tuning_result = tuning.tune_xgboost(
            enriched,
            feature_cols=selected_features,
            param_grid=param_grid,
            target_col="pm2_5",
            groups_col="city",
        )
        for combo in tuning_result["cv_results"]:
            grid_params = combo["params"]
            run_name = (
                f"{selector_name}_depth_{grid_params['max_depth']}_"
                f"lr_{grid_params['learning_rate']}"
            )
            run_params = {
                **grid_params,
                "feature_selection": selector_name,
                "missing_threshold": missing_threshold,
            }
            run_id = tracking.log_run(
                run_name=run_name,
                params=run_params,
                metrics={
                    "rmse": combo["rmse"],
                    "mae": combo["mae"],
                    "r2": combo["r2"],
                },
            )
            logged_runs.append((run_name, run_id))

    print(f"Logged {len(logged_runs)} XGBoost grid runs to MLflow.")
    for run_name, run_id in logged_runs:
        print(f"- {run_name}: {run_id}")




if __name__ == "__main__":
    main()
