# Module 1 — Rigorous Correlation Analysis

**Question:** Compare `correlation_table` to what you found in the Session 2 discovery notebook, which only used Kampala and Nairobi. Did any variable’s apparent importance change now that Lagos and Bujumbura are included? Does the most correlated variable have a large enough `n` for you to trust it? What would you investigate next?

## Answer

The Session 2 heatmap suggested that `nitrogendioxide_no2_column_number_density` and `carbonmonoxide_co_column_number_density` had the strongest positive relationships with `pm2_5`, with correlations around 0.3. That remains broadly true after adding Lagos and Bujumbura, but their ordering changes: CO becomes the strongest Pearson correlate (r ≈ 0.42), followed by NO₂ (r ≈ 0.40). The correlation for CO also increases from about 0.31 in Kampala and Nairobi to about 0.42 across all four cities.

The most noticeable change is the absorbing aerosol index. Its Pearson correlation with `pm2_5` was close to zero for Kampala and Nairobi (r ≈ 0.01), but rises to about 0.17 across all four cities. Cloud fraction moves the other way, from a small positive correlation (about 0.07) to a value close to zero. These changes suggest that the relationships may differ across cities; they do not establish that adding the cities caused a general improvement in predictive usefulness.

CO, the top-ranked variable, has **n = 4,441** pairwise-complete observations, so its correlation is not based on just a handful of rows. That is a reasonably large sample for estimating an overall association. Still, I would not treat it as conclusive: observations from the same city and nearby dates may not be independent, and a pooled correlation can reflect differences between cities rather than a within-city relationship. The very small p-value indicates evidence against zero correlation under the test’s assumptions, but it does not measure practical importance or prove causation.

Next, I would compare Pearson and Spearman results, inspect the CO–PM2.5 scatterplot for outliers and nonlinearity, and calculate the relationship separately for each city. I would also check whether the direction and strength persist under city-held-out evaluation and investigate the high-missingness columns and multiple comparisons. This would show whether the pooled associations are consistent enough to inform feature selection or modeling.
