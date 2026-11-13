# Module 2 — Advanced Cleaning
Question: Why does dropping high-missing columns have to happen before the per-city fill, not after? 

`fill_missing_by_city` uses forward-fill + backward-fill within each city. If a column is 80% missing, the fill will stretch its few real values across the entire time series — the result is a mostly-constant column that looks complete but carries almost no real signal. If you ran columns_above_missing_threshold on that already-filled data, it would see 0% missing and keep the column as a feature. The fill has masked the missingness, so the threshold check becomes blind to exactly the columns it was meant to catch. Dropping first preserves the missingness information that the threshold relies on.

What would columns_above_missing_threshold report if you ran it on already-filled data instead? 

An empty list. After ffill().bfill(), every fillable column has zero NaNs, so no column exceeds any threshold. The high-missing columns are invisible to the check — the fill has already "fixed" them in a way that destroys the signal rather than recovering it.

And why threshold 0.7 specifically — what would change with a lower threshold, like 0.5?

0.7 is a judgment call: a column with >70% missing values is so sparse that ffill/bfill would be interpolating across huge gaps, producing values that are mostly just the last-seen reading repeated. At 0.5, you'd drop more columns (anything over 50% missing), keeping fewer features but with higher fill quality — the remaining gaps are small enough that forward/backward fill is a reasonable approximation. At 0.7, you retain more features, but columns in the 50–70% range are kept and filled across large gaps, which is questionable. The exact value is somewhat arbitrary; in practice you'd inspect the actual missingness patterns in your data and pick a threshold where the fill quality is still defensible.