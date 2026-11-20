# Module 9 — Model Registry

The numbers below come from my run of `uv run python scripts/register_champion.py`, which registers Module 7’s pipeline (`AirQualityCleaner(missing_threshold=0.6)` → `RFE(n_features_to_select=8)` → model) twice as versions of `air_quality_model`, scored with `cross_val_score` and `GroupKFold` over the four cities.

## Question 1

**Question:** Which model became `champion` in your own run, `LinearRegression` or `Ridge`? Is that consistent with your Module 7 reflection?

**Answer:** **Ridge** became champion, as version 2 of `air_quality_model`:

| Version | Model | Mean RMSE (GroupKFold) |
|---|---|---:|
| 1 | `LinearRegression` | 1,321.24 |
| 2 | `Ridge` | 29.26 |

This is exactly what Module 7 predicted, down to the same numbers: the script rebuilds the same pipeline on the same folds. In Module 7, the `LinearRegression` mean was destroyed by the Kampala fold alone (RMSE 5,189.84): its RFE kept two near-identical azimuth angles with opposite coefficients of ±440.8, and a few imputed rows in Kampala broke their cancellation. Ridge’s L2 penalty keeps coefficients small, so that fold drops to 15.55.

The decision deserves one caveat. The mean RMSE rewards Ridge for robustness on one fold, not for being better everywhere: on Nairobi, Lagos and Bujumbura, `LinearRegression` was slightly better (25.69, 51.52 and 17.92 against 26.00, 55.13 and 20.36). I would still promote Ridge, because a model that occasionally predicts −78,221 µg/m³ cannot be served. The registered version is then refit on all four cities; the 29.26 is an estimate of how it should generalize, not a score of the registered fit itself.

## Question 2

**Question:** If the prediction code loaded `models:/air_quality_model/2` (a fixed version number) instead of `models:/air_quality_model@champion`, what would break the next time a better model is registered? What does the alias’s indirection give you that a plain version number does not?

**Answer:** Nothing would fail loudly, and that is the problem. A better model registered tomorrow becomes version 3 and is promoted, but code pinned to version 2 keeps loading the old Ridge, silently. To serve version 3, someone has to edit the loading code, review it and redeploy it, and do it again at every promotion and every rollback. If version 2 were ever deleted, the same code would start failing at load time instead.

The alias separates two decisions that a version number ties together. *Which* model to serve becomes a registry decision, made where the evaluation happens: `register_champion.py` compares the candidates and moves `champion`. *How* to load it stays in the code, written once as `load_champion("air_quality_model")`. Promoting or rolling back is then a single `set_registered_model_alias` call, with no code change, and every earlier version stays registered, so rolling back means moving the alias back. The registry also answers “what is in production?” directly: `get_model_version_by_alias("air_quality_model", "champion")` returns version 2.

That indirection has a cost: moving the alias changes what every consumer loads immediately, without any code review. The safeguard therefore has to live in the promotion step. Mine is only partial: the script promotes the better of the two candidates *it just trained*, even if an earlier champion scored better. A stricter version would compare each candidate with the current champion before moving the alias.
