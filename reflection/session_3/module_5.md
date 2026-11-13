# Module 5 — Hyperparameter Tuning

**Question:** Compare four numbers: the untuned `XGBRegressor`, the worst combination in the grid, the best combination, and Module 4’s `LinearRegression` on the same 8 columns. Was it worth introducing a more complex model here? What does the gap between the best and worst combination tell you about why tuning matters, independently of which model you picked?

## Answer

Using GroupKFold on the same eight RFE-selected columns, the untuned `XGBRegressor` had a mean RMSE of **31.88**. The worst of the four grid combinations scored **31.07** (`max_depth=5`, `learning_rate=0.2`), while the best scored **27.57** (`max_depth=3`, `learning_rate=0.05`). Module 4’s `LinearRegression` on these eight columns scored **27.63**.

The tuned XGBoost model is only about **0.06 RMSE** better than LinearRegression. That difference is tiny compared with the variation across held-out cities (the tuned model’s RMSE standard deviation is about 14.57), so these results alone do not justify the additional model and tuning complexity. I would keep the simpler linear model unless further validation or a meaningful operational goal showed that the small improvement matters.

The **3.50 RMSE** gap between the best and worst grid settings shows that performance depends substantially on the hyperparameters, even when the model family and features stay fixed. The untuned default was worse still. Tuning matters because a flexible model can perform quite differently under different settings; choosing a model family alone does not guarantee good performance. This conclusion is limited to the small grid tested here, not every possible XGBoost configuration.
