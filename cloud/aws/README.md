# AWS deployment option

The same pipeline can use Amazon S3 as the landing zone instead of the Databricks DBFS path used in the local demo.

Suggested layout:

```text
s3://<bucket>/concrete-quality/raw/
    plants.csv
    materials.csv
    plant_materials.csv
    production.csv
    quality_tests.csv
```

Databricks can read the landing zone with an S3 URI, for example:

```python
RAW_PATH = "s3a://<bucket>/concrete-quality/raw"
```

For production, use an IAM role / instance profile rather than hard-coded AWS keys. The Snowflake layer can also use an external S3 stage if the organization wants Snowflake to load directly from the same landing zone.

The repository intentionally contains no credentials or account-specific infrastructure.
