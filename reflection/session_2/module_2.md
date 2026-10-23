# Module 2 — Build a First Pipeline
Question: Run the pipeline again, but train on Nairobi and test on Kampala instead. Compare the two RMSE values. What does the difference tell you about how well a model generalizes from one city to another? Would you trust either direction enough to deploy it?

Train City : Kampala 
Test City : Nairobi
RMSE: 21.459
MAE:  9.983
R²:   -0.024

Train City : Nairobi  
Test City : Kampala
RMSE: 15.249
MAE:  10.515
R²:   -0.099

## Reflection

The model has a lower RMSE when trained on Nairobi and tested on Kampala (15.249) than when trained on Kampala and tested on Nairobi (21.459). This shows that transfer between the two cities is asymmetric: the model's errors depend on which city it learns from and which city it is applied to. The difference suggests that the relationship between the satellite measurements and PM2.5 is not identical across the cities, or that their data distributions differ.

I would not trust either direction enough to deploy the model. Both R² values are negative, so in each case the model performs worse than a simple prediction using the test city's mean PM2.5. The RMSE difference alone does not establish reliable generalization, especially with only one sampled train/test split per direction. I would want more validation across time and locations, and a model evaluated on representative data from both cities, before considering deployment.

## CRISP-DM phases

**Question:** Across [Understand the Air Quality Problem](https://hub.imt-atlantique.fr/datascience-toolkit/session2/practical_1) and this activity, which CRISP-DM phases have you already gone through? Which phase does building and evaluating this baseline pipeline itself belong to?

Across the two activities, I have worked through Business Understanding by framing the air-quality problem and the goal of predicting PM2.5; Data Understanding by exploring the cities, measurements, distributions, correlations, and missing values; and Data Preparation by filtering and sampling the data, handling missing values, splitting by city, and creating date-based features. Building the baseline Linear Regression model belongs to the Modeling phase. Measuring its RMSE, MAE, and R² and comparing results across cities belongs to Evaluation. Deployment has not been reached: the results do not yet justify using the model in practice.

