# Module 3 — Robust Evaluation

### Score Tables

#### Summary of Results across Pipeline Changes

| Step / Setting | Split / Evaluation | RMSE | MAE | R² | Description |
|---|---|---|---|---|---|
| **Session 2** — Manual Split 1 | Train Kampala → Test Nairobi (max 1200 rows) | **24.6** | ~10.5 | **-0.02** | Naive fill (`ffill/bfill`). Direction-dependent; R² < 0. |
| **Session 2** — Manual Split 2 | Train Nairobi → Test Kampala (max 1200 rows) | **15.2** | **10.5** | **-0.10** | Reversed direction yields completely different metrics. |
| **Session 3 (Mod. 2)** — Naive Fill | Train Kampala → Test Bujumbura | **CRASH** | — | — | Bujumbura has columns entirely NaN; cannot fill. |
| **Session 3 (Mod. 2)** — Drop >0.7 threshold + Fill | Train Kampala → Test Bujumbura | **19.18** | **12.03** | **+0.26** | Dropping sparse columns before filling restores signal. |
| **Session 3 (Mod. 3)** — GroupKFold CV (Global) | 4-city Leave-One-Group-Out CV (`LinearRegression`) | **27.58** *(± 14.71)* | **13.82** *(± 5.34)* | **+0.09** *(± 0.09)* | Systematic evaluation across all 4 cities without leakage. |

#### Per-City Breakdown (`GroupKFold` on all 4 cities)

| Tested City (Held-out Fold) | RMSE | MAE | R² | Notes |
|---|---|---|---|---|
| **Kampala** | **13.40** | 9.67 | +0.13 | Easiest city to predict; well-populated in training set. |
| **Bujumbura** | **19.74** | 12.61 | +0.21 | Smallest dataset (123 rows), consistent generalization. |
| **Nairobi** | **25.19** | 10.15 | -0.02 | Moderate error, negative R². |
| **Lagos** | **52.01** | 22.87 | +0.03 | Highest error (outlier / catastrophic domain shift). |
| **Aggregated (Mean ± Std)** | **27.58 ± 14.71** | **13.82 ± 5.34** | **0.09 ± 0.09** | True regional generalization metric. |

---

### Questions & Reflection

**Question:** Which city has the highest RMSE when held out? Does the mean RMSE across all four folds match either of Session 2’s two numbers? What does a large std across folds tell you about how much you should trust a performance number computed from a single train/test pair, the way Session 2 did?

- **City with the highest RMSE:** **Lagos** has by far the highest RMSE at **52.01** (compared to Kampala: 13.40, Bujumbura: 19.74, Nairobi: 25.19). It is nearly 4x worse than Kampala, showing that predicting pollution levels in Lagos from the other three cities is significantly harder due to local dynamics and differing geographic context.

- **Comparison with Session 2 numbers:** No, the mean RMSE across all four folds (**27.58**) does not match either of Session 2's numbers:
  - Session 2's Train Kampala → Test Nairobi gave **24.6**.
  - Session 2's Train Nairobi → Test Kampala gave **15.2**.
  Neither single pair captured the true overall performance. Testing on Kampala happened to be the easiest possible case (RMSE 13.40 / 15.2), creating an overly optimistic illusion, while neither run ever evaluated on Lagos (52.01) or Bujumbura (19.74).

- **What the large std tells us:** The large standard deviation (**± 14.71**, more than 53% of the mean) indicates high variance across groups and extreme sensitivity to which city is held out. This proves that a performance number computed from a single manual train/test pair cannot be trusted: depending on the pair chosen and direction of the split, you get a fragile and misleading estimate with no guarantee of generalization to other groups. Only a group-aware cross-validation like `GroupKFold` reveals both the true mean performance and the variability across unseen groups.
