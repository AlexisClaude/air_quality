# Module 6 — Experiment Tracking

**Question:** Sort the Runs table by `rmse`. Which combination won — does it match what Module 5 already told you? Would you have found that as quickly by rereading Module 5’s printed `cv_results` table? At roughly how many runs does “just re-run and read the terminal” stop being practical for you?

## Answer

Sorting the MLflow Runs table by ascending `rmse`, the best combination is **RFE feature selection**, `max_depth=3`, `learning_rate=0.05`, with `missing_threshold=0.7`. Its mean RMSE is **27.57**. This matches Module 5, where the same XGBoost settings were the best grid combination on the RFE-selected features. The best SelectKBest combination was close, at RMSE **27.61**, but did not win.

For only four grid combinations, I could find the winner quickly in Module 5’s printed `cv_results` table. The MLflow table is more useful as experiments accumulate: I can sort and filter by RMSE, feature-selection method, or other logged parameters without rerunning the search or scanning terminal output. In this local experiment, 24 runs are visible, including repeated runs from executing the script more than once; those repeated entries also show why run history needs to be interpreted carefully.

For me, reading terminal output would stop being practical at roughly **20–30 runs**, especially once runs vary across more than one dimension, such as model, feature selector, and preprocessing threshold. The exact point depends on how many metrics and parameter combinations need comparison, but by that scale a sortable, searchable run table is easier to use and less error-prone.
