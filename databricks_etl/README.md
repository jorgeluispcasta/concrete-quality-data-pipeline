# Databricks ETL

Run the scripts in order.

```text
01_bronze.py
      ↓
02_silver.py
      ↓
03_gold.py
      ↓
04_acquisition_analysis.py
```

The scripts assume a Databricks environment with a Spark session available as `spark`. They write Delta tables to the configured DBFS paths.
