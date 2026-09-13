from pyspark.sql import functions as F

RAW_PATH = "dbfs:/FileStore/concrete_quality/raw"
BRONZE_PATH = "dbfs:/FileStore/concrete_quality/bronze"

FILES = ["plants", "materials", "plant_materials", "production", "quality_tests"]


def load_to_bronze(name: str) -> None:
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(f"{RAW_PATH}/{name}.csv")
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("source_file", F.lit(f"{name}.csv"))
    )
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{BRONZE_PATH}/{name}")


for file_name in FILES:
    load_to_bronze(file_name)

print("Bronze layer created successfully.")
