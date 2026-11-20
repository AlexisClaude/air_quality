# Module 7 — A Scikit-learn Transformer

All numbers below come from my own run of `run_advanced` (`uv run python scripts/run_pipeline.py`): `AirQualityCleaner(missing_threshold=0.6)` → `RFE(n_features_to_select=8)` → model, evaluated with `GroupKFold` on Kampala, Nairobi, Lagos and Bujumbura (8,071 rows).

## Question 1

**Question:** If `ColumnMeanImputer.fit` took its means from somewhere other than `X` (a global variable, a file), would `clone()` still protect you against leakage between folds? Why or why not?

**Answer:** No. `clone()` only rebuilds a fresh, unfitted instance from the constructor parameters returned by `get_params()`. It erases what the previous fold learned, but it has no control over what `fit` reads. If `fit` loads means computed on the full dataset, every fresh clone reads the same values again, and those values already include the validation rows. Every fold would leak, silently, while each fold would still look properly separated.

The protection therefore comes from two parts working together. `Pipeline` and `cross_val_score` guarantee that `fit` receives only the training rows of the fold; the transformer must keep its side of the contract by learning from that `X` and nothing else.

## Question 2

**Question:** Why are Module 2’s missingness threshold and Module 4’s `RFE` selection, each computed once on the whole dataset before any fold split, exactly the same structural problem as the badly written `fit` above?

**Answer:** Both are decisions learned from data: which columns are too incomplete to keep, and which eight features are worth keeping. In Modules 2–5, I computed them once on all four cities and only refit the model inside each fold. The held-out city had therefore already helped decide which columns survived, exactly like a `fit` that reads its means from a global variable instead of from the fold’s `X`.

My run shows that this decision really depends on the training cities at 0.6. Computed on all four cities, the threshold drops 28 columns, including the nine `sulphurdioxide_*` columns. Learned per fold, the cleaner still drops 28 columns when Lagos or Bujumbura is held out, but only 19 when Kampala or Nairobi is held out: the SO₂ columns are then kept, and RFE selects three of them in both folds. The global computation would have hidden this difference. At 0.7, the leak had no visible effect because the only columns above the threshold, the `uvaerosollayerheight_*` family, are 93–100 % missing in every city (94.7 % overall); the process was just as flawed, but that threshold did not expose it.

## Question 3

**Question:** Look at your own run’s results per fold, not just the mean: is every fold in the same range, or does one stand out? If one does, what is different about that fold’s training cities?

**Answer:** One fold stands out by several orders of magnitude, which makes the mean meaningless:

| Held-out city | RMSE | MAE | R² |
|---|---:|---:|---:|
| Kampala | 5,189.84 | 366.71 | −130,879.36 |
| Nairobi | 25.69 | 10.48 | −0.06 |
| Lagos | 51.52 | 23.97 | 0.05 |
| Bujumbura | 17.92 | 11.97 | 0.35 |

The mean RMSE is 1,321.24 (std 2,233.57), but it describes none of the folds. The Kampala fold is the only one whose training set is a minority of the data: it trains on Nairobi, Lagos and Bujumbura (2,475 rows) and predicts Kampala (5,596 rows, 69 % of the dataset). PM2.5 itself is not unusually hard to predict in Kampala: it is actually the most regular city (mean 22.8, std 14.3).

The failure comes from what the model learns on those three training cities. With the SO₂ columns kept, RFE selects groups of nearly redundant variables: three SO₂ densities, two HCHO densities, and two satellite angles, `uvaerosolindex_sensor_azimuth_angle` and `ozone_sensor_azimuth_angle`. In the training rows, these two angles are practically identical (correlation 1.0, maximum difference 0.011°). `LinearRegression` gives them opposite coefficients, −440.8 and +440.8, which cancel out in training. In Kampala, however, `ozone_sensor_azimuth_angle` is missing in 108 rows and filled forward/backward within the city. In 25 of those rows, the filled value differs from the actual aerosol angle by more than 10°, up to 177.5°, so the cancellation breaks and the prediction falls as low as −78,221. Only 68 of 5,596 rows have an error above 200; without them, the fold’s RMSE would be 15.56.

I see the large weights on near-duplicate features as the underlying cause, and the imputed rows as the trigger. The Lagos fold, the second worst, is a different case: Lagos has the widest PM2.5 spread (std 52.8, max 419.5), so a larger error there is expected even from a stable model.

## Question 4

**Question:** Swap the model for `Ridge`, both as `RFE`’s estimator and as the final model, and rerun. Does anything change, and why might a regularized model behave differently here than a plain `LinearRegression`?

**Answer:** Yes, the Kampala fold stops exploding. With `Ridge(alpha=1.0)` in both places, the folds give:

| Held-out city | `LinearRegression` RMSE | `Ridge` RMSE |
|---|---:|---:|
| Kampala | 5,189.84 | 15.55 |
| Nairobi | 25.69 | 26.00 |
| Lagos | 51.52 | 55.13 |
| Bujumbura | 17.92 | 20.36 |
| Mean (std) | 1,321.24 (2,233.57) | 29.26 (15.39) |

The mean drops from 1,321.24 to 29.26 because Kampala goes from 5,189.84 to 15.55; the other three folds actually get slightly worse. Ridge adds an L2 penalty on coefficient size. When two features carry almost the same signal, `LinearRegression` can fit huge opposite weights that cancel on the training rows; Ridge prefers small weights spread across them. In the Kampala fold, the largest absolute coefficient falls from 41,902.8 to 129.1. Because `RFE` ranks features by the same coefficients, Ridge also changes the selection: the duplicate pair of azimuth angles disappears, and `hour`, ozone and cloud variables enter the selection. A small error in one input can then no longer be amplified into an absurd prediction.

That stability has a cost: the bias added by the penalty slightly degrades the three folds that were already stable. Ridge also treats the root cause only partially. The features are not standardized, so the same `alpha` penalizes very differently a density around 10⁻⁴ and an angle in degrees; adding a `StandardScaler` before `RFE` would make the penalty comparable across features. The per-fold scores remain the main lesson: only by reading them could I see that a single city was driving the mean.
