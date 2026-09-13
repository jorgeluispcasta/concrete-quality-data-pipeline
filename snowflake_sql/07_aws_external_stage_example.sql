-- Optional production pattern when Snowflake loads the same files directly from S3.
-- Replace placeholders with environment-specific values and use a Snowflake storage integration.

CREATE OR REPLACE STAGE CONCRETE_ANALYTICS.RAW.S3_RAW_STAGE
    URL = 's3://<bucket>/concrete-quality/raw/'
    STORAGE_INTEGRATION = <STORAGE_INTEGRATION_NAME>
    FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');
