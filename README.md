# concrete-quality-data-pipeline

An end-to-end data engineering project inspired by a real manufacturing quality standardization problem in concrete production.

The project simulates production and quality data from a network of concrete plants, standardizes the data, calculates operational KPIs, and identifies potential acquisition targets using quality, rework, material similarity and geographic proximity.

## Architecture

```text
Synthetic CSV data
       |
       v
Python data generation
       |
       v
Databricks / PySpark
Bronze -> Silver -> Gold
       |
       v
Snowflake
Star schema + analytics views
       |
       v
Power BI
Quality / Operations / Acquisition
```

## Tech stack

- Python / Pandas / NumPy
- SQL
- Databricks / PySpark / Delta Lake
- Snowflake
- Power BI / DAX

## Business questions

- Which plants consistently produce within quality requirements?
- Where is rework creating cost?
- Which plants have the strongest operational performance?
- Which target plants are strategically attractive based on quality, materials and proximity?

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python data_simulation/run_all.py
python analytics/quality_analysis.py
python analytics/plant_performance.py
python analytics/acquisition_analysis.py
pytest -q
```

The local Python layer creates the CSV data and analytics outputs under `data/`.

## Databricks

Upload `data/raw/*.csv` to the configured raw location and run these scripts in order:

1. `databricks_etl/01_bronze.py`
2. `databricks_etl/02_silver.py`
3. `databricks_etl/03_gold.py`
4. `databricks_etl/04_acquisition_analysis.py`

The scripts use Delta Lake and are written for a Databricks notebook/job environment where `spark` is available.

## Snowflake

Run the SQL files in order:

1. `snowflake_sql/01_database.sql`
2. `snowflake_sql/02_raw_tables.sql`
3. Upload the generated CSV files to `RAW.RAW_STAGE`
4. `snowflake_sql/03_load_raw.sql`
5. `snowflake_sql/04_star_schema.sql`
6. `snowflake_sql/05_analytics.sql`
7. `snowflake_sql/06_validation.sql`

## Dashboard

The Power BI design and DAX measures are in `powerbi_dashboard/`.

## Data note

All company, plant, supplier and production data in this repository are fictional. The project is a portfolio reconstruction of a manufacturing analytics use case and does not contain proprietary historical data.
