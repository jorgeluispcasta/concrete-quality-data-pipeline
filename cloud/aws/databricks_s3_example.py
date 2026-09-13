from pyspark.sql import functions as F

RAW_PATH = "s3a://<bucket>/concrete-quality/raw"

production = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{RAW_PATH}/production.csv")
    .withColumn("ingestion_timestamp", F.current_timestamp())
)

production.show(5)
