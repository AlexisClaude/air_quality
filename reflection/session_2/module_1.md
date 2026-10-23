# Module 1 — Understand the Air Quality Problem

## Question 1: What information is already available in the problem statement? What is missing (e.g., how many monitoring stations, over what time period, how PM2.5 was measured on the ground)?

The problem statement tells us that:

- the target is ground-level **PM2.5**, particulate matter with a diameter below
  2.5 micrometres;
- the predictors include satellite observations from Sentinel-5P;
- the dataset concerns two cities: **Kampala** and **Nairobi**;
- each observation has a date, an hour, monitoring-site coordinates, a ground PM2.5
  value, and several atmospheric measurements such as SO2, CO, NO2, HCHO, aerosol
  index, O3, aerosol-layer height, and cloud fraction.

Important information is still missing or should be verified:

- the exact number of monitoring stations in each city and whether a row represents
  a station, a station-day, or a station-hour;
- the complete observation period, its time zone, and whether there are gaps in
  the time series;
- the instrument used for ground PM2.5, its calibration, units, detection limit,
  averaging period, and quality-control procedure;
- the exact satellite product versions, spatial resolution, overpass time, units,
  missing-data rules, and how satellite pixels were matched to monitoring sites;
- the amount and pattern of missing data and the number of usable observations;
- whether the same sites and dates occur in both the training and test sets.

Without this information, it is difficult to assess measurement error, temporal
representativeness, and whether the evaluation is genuinely independent.

## Question 2: Who would use a model that predicts PM2.5 from satellite data, and for what decision? What would make such a model trustworthy to them?

Potential users include public-health agencies, city authorities, environmental
regulators, researchers, hospitals, and organisations that need pollution
information in places without dense ground-monitoring networks. They could use the
model to identify pollution hotspots, issue health alerts, inform traffic or
industrial restrictions, plan new monitoring stations, estimate population
exposure, or evaluate air-quality policies.

The model would be trustworthy if it:

- is evaluated on data from unseen dates, sites, and ideally an unseen city;
- reports uncertainty intervals, not only a single prediction;
- has acceptable error for the intended decision, especially at high-pollution
  levels;
- is calibrated and its errors are not systematically worse for one city,
  season, neighbourhood, or weather condition;
- uses measurements with documented units and quality control;
- remains reliable when satellite data are missing or cloud conditions change;
- is compared with simple baselines and periodically checked against new ground
  measurements.

Trust therefore requires both good predictive accuracy and evidence that the model
generalises to the situations in which it will actually be used.

## Question 3: `pm2_5` is the target variable. Which other variables do you expect to be genuinely informative predictors, and which ones look more like identifiers than physical measurements?

The atmospheric satellite variables are plausible predictors because they describe
pollution or atmospheric conditions related to PM2.5:

- SO2, CO, NO2, HCHO, and O3 column number densities;
- absorbing aerosol index;
- aerosol-layer height;
- cloud fraction, which may also capture retrieval quality and atmospheric
  conditions.

Time variables can also be informative. Pollution may vary by hour, season, and
day of week, so `date` can be transformed into month or other temporal features,
and `hour` can be represented as a cyclical feature. `city` may capture broad
geographical and emission differences, although it can also become a shortcut
for memorising the training locations.

`index` is an identifier or row label, not a physical measurement, and should not
be used as a predictor. `site_latitude` and `site_longitude` are real geographic
measurements, but in this dataset they may function mainly as site identifiers
when there are only a few fixed sites. They should therefore be handled carefully:
including them can cause the model to memorise Kampala coordinates and fail on
Nairobi rather than learn transferable pollution relationships.

## Question 4: Suppose you train a model only on Kampala data. What could go wrong when you apply it to Nairobi? List at least two concrete risks.

Several forms of distribution shift are possible:

1. **Different emission sources and levels.** Traffic, industry, domestic fuel use,
   fires, and urban density may differ between the cities. The same satellite
   concentration can therefore correspond to a different ground-level PM2.5
   value.
2. **Different geography and meteorology.** Terrain, altitude, wind, humidity,
   rainfall, and atmospheric mixing can change the relationship between a column
   measurement and near-surface pollution.
3. **Different monitoring sites or sampling.** Nairobi sites may be located in
   environments not represented in Kampala, such as different road, residential,
   or background settings. A model may not extrapolate safely to those locations.
4. **Covariate and measurement shift.** Satellite coverage, cloudiness, missing
   values, retrieval quality, instruments, or calibration may differ between the
   cities.

Consequently, predictions in Nairobi may be biased, errors may be much larger than
the Kampala validation error, and high-pollution episodes may be missed. A city-held
out evaluation and uncertainty monitoring are necessary before operational use.

## Question 5: Describe the expected type, measurement scale, and analytical role of every variable.

| Variable | Expected type | Measurement scale | Analytical role |
|---|---|---|---|
| `index` | Integer | Nominal identifier | Row/index label only; exclude from predictors. |
| `city` | String/categorical | Nominal | Location group, stratification variable, or domain indicator; not a numeric measurement. |
| `date` | Datetime | Temporal | Observation time; use to create season, month, day-of-week, and to make chronological splits. |
| `hour` | Integer/discrete | Cyclical temporal | Hour of observation; useful for daily pollution patterns, preferably encoded cyclically. |
| `site_latitude` | Continuous float | Geographic interval | Monitoring-site location; useful for spatial analysis, but can act as a site identifier and cause poor transfer. |
| `site_longitude` | Continuous float | Geographic interval | Monitoring-site location; same caution as latitude. |
| `pm2_5` | Continuous float | Ratio | Target variable: ground PM2.5 concentration, normally expressed in mass per volume. |
| `sulphurdioxide_so2_column_number_density` | Continuous float | Ratio | Satellite atmospheric pollutant predictor. |
| `carbonmonoxide_co_column_number_density` | Continuous float | Ratio | Satellite atmospheric pollutant predictor. |
| `nitrogendioxide_no2_column_number_density` | Continuous float | Ratio | Satellite atmospheric pollutant predictor and possible traffic/combustion proxy. |
| `formaldehyde_tropospheric_hcho_column_number_density` | Continuous float | Ratio | Satellite atmospheric pollutant/emission predictor. |
| `uvaerosolindex_absorbing_aerosol_index` | Continuous float | Interval-like index | Aerosol-related satellite predictor; its sign and magnitude describe absorbing aerosol conditions, but it is not a direct PM2.5 concentration. |
| `ozone_o3_column_number_density` | Continuous float | Ratio | Satellite atmospheric pollutant predictor. |
| `uvaerosollayerheight_aerosol_height` | Continuous float | Ratio-like physical measure | Atmospheric structure and dispersion predictor; may help distinguish elevated aerosol layers from near-surface pollution. |
| `cloud_cloud_fraction` | Continuous float bounded between 0 and 1 | Ratio | Cloudiness and satellite-retrieval-quality predictor; may also be used for filtering or missingness analysis. |

The exact units and valid ranges should be confirmed in the data dictionary. In
particular, satellite **column** measurements describe the atmospheric column and
are not automatically equivalent to the concentration measured at the ground.
