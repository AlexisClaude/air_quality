# Module 4 — Feature Selection

**Question:** RFE’s 8 columns come close to matching (or beating) the RMSE you saw in Module 3 with the 8 hand-picked DEFAULT_COLUMNS — an algorithm rediscovered, on its own, roughly what a human chose by inspection. Why does SelectKBest do noticeably worse here despite also picking 8 columns? What does this tell you about when a univariate method is enough, and when it is not? Cite one concrete number from your own run showing why the all-features model should not be trusted.

**Answer**

With GroupKFold, the 8 features selected by RFE give a mean RMSE of **27.63**, very close to the **27.58** I obtained in Module 3 with the hand-picked `DEFAULT_COLUMNS`. `SelectKBest` gives a noticeably higher mean RMSE of **32.84**, even though it also selects eight features.

The difference is that `SelectKBest` scores each feature against `pm2_5` independently. It can therefore select several features that appear individually useful but carry nearly the same information. In my run, it selected four `solar_azimuth_angle` variables; these are highly redundant proxies for satellite geometry and correlate with one another at roughly **0.98–0.99**. That uses half of the eight-feature budget on essentially the same signal. RFE repeatedly fits a model using the features that remain, so redundant features add less once a similar feature is already present. Its selected set instead includes more distinct pollutant measurements.

A univariate method can be enough when the candidate features are reasonably independent and the goal is to rank each feature's individual association with the target. It is less suitable when predictors are strongly correlated: it cannot account for redundancy or for how useful a feature is in the context of the other selected features. A multivariate approach such as RFE can account for those interactions between predictors, though its selected features still depend on the estimator and dataset.

The all-features model is not trustworthy here: using all 66 candidates produced a mean GroupKFold RMSE of **3,995.03**, while PM2.5 in this dataset ranges only from about **1.2 to 456.2**. Its mean R² was **−306,446.82**. The extremely poor held-out performance is consistent with multicollinearity making the linear model's coefficients unstable and damaging its ability to generalize.
