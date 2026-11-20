"""Scikit-learn-compatible transformers for the Air Quality pipeline."""

from sklearn.base import BaseEstimator, TransformerMixin

from air_quality import data, features


class AirQualityCleaner(BaseEstimator, TransformerMixin):
    """
    Drop columns missing above `missing_threshold`, then fill what remains
    per city — as a proper scikit-learn transformer: `fit` decides which
    columns to drop using only the rows it is given, `transform` applies
    that frozen decision to whatever rows it is given next.

    This matters inside a Pipeline evaluated with GroupKFold: `fit` only ever
    sees the fold's training cities, so a city held out for validation never
    influences which columns get dropped for that fold — unlike calling
    columns_above_missing_threshold once on the whole dataset before any
    fold split (Modules 2-5), which lets every fold's "held-out" city quietly
    influence its own evaluation.

    Parameters:
    - missing_threshold: fraction of missing values (between 0 and 1) above
      which a column is dropped

    Learned attribute:
    - columns_to_drop_: set by fit(), the column names to drop in transform()
    """

    def __init__(self, missing_threshold: float = 0.7):
        self.missing_threshold = missing_threshold

    def fit(self, X, y=None):
        """
        Learn which columns to drop, using only X — never any other data.

        Parameters:
        - X: DataFrame to learn the drop decision from (a fold's training rows)
        - y: ignored, present only for scikit-learn's fit(X, y) contract

        Returns:
        - self, so fit can be chained as fit(X).transform(X)
        """
        self.columns_to_drop_ = data.columns_above_missing_threshold(
            X, threshold=self.missing_threshold
        )
        return self

    def transform(self, X):
        """
        Apply the frozen drop decision from fit(), then fill what remains
        per city.

        Parameters:
        - X: DataFrame to clean — may be different rows than what fit() saw
          (e.g. a validation fold, or genuinely new data)

        Returns:
        - DataFrame of numeric feature columns only (see features.feature_columns),
          with self.columns_to_drop_ removed and missing values filled per city
        """
        cleaned = data.drop_columns(X, self.columns_to_drop_)
        fillable_columns = [
            column for column in cleaned.columns if column not in ("city", "date")
        ]
        cleaned = data.fill_missing_by_city(cleaned, fillable_columns)
        # fill_missing_by_city sorts by city/date; a transformer must preserve
        # row order so X remains aligned with y inside a scikit-learn Pipeline.
        cleaned = cleaned.loc[X.index]
        return cleaned[features.feature_columns(cleaned)]
