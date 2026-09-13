from pyspark.sql import functions as F

SILVER_PATH = "dbfs:/FileStore/concrete_quality/silver"
GOLD_PATH = "dbfs:/FileStore/concrete_quality/gold"

plants = spark.read.format("delta").load(f"{SILVER_PATH}/plants")
plant_materials = spark.read.format("delta").load(f"{SILVER_PATH}/plant_materials")
production_quality = spark.read.format("delta").load(f"{SILVER_PATH}/production_quality")

plant_performance = (
    production_quality
    .groupBy("plant_id")
    .agg(
        F.countDistinct("production_id").alias("production_batches"),
        F.sum("volume_m3").alias("total_volume_m3"),
        F.avg("strength_28d_mpa").alias("avg_strength_mpa"),
        F.stddev("strength_28d_mpa").alias("strength_stddev_mpa"),
        F.avg(F.col("quality_pass").cast("double")).alias("quality_pass_rate"),
        F.avg(F.col("rework_flag").cast("double")).alias("rework_rate"),
        F.sum("rework_cost_cad").alias("rework_cost_cad"),
        F.avg("process_efficiency").alias("avg_process_efficiency"),
        F.sum("material_cost_cad").alias("material_cost_cad"),
    )
    .join(plants.select("plant_id", "plant_name", "region", "latitude", "longitude", "annual_capacity_m3"), "plant_id")
    .withColumn("capacity_utilization", F.col("total_volume_m3") / F.col("annual_capacity_m3"))
    .withColumn("quality_consistency", 1 / (1 + F.coalesce(F.col("strength_stddev_mpa"), F.lit(99.0))))
)

monthly_quality = (
    production_quality
    .withColumn("month", F.date_format("production_date", "yyyy-MM"))
    .groupBy("plant_id", "month")
    .agg(
        F.sum("volume_m3").alias("volume_m3"),
        F.avg(F.col("quality_pass").cast("double")).alias("quality_pass_rate"),
        F.avg(F.col("rework_flag").cast("double")).alias("rework_rate"),
        F.avg("strength_28d_mpa").alias("avg_strength_mpa"),
        F.sum("rework_cost_cad").alias("rework_cost_cad"),
    )
)

material_profiles = (
    plant_materials
    .groupBy("plant_id")
    .pivot("material_group", ["Cement", "Fine Aggregate", "Coarse Aggregate", "Clay", "Admixture"])
    .agg(F.first("material_id"))
)

# Acquisition score: quality, consistency, rework, efficiency and capacity utilization.
score = (
    plant_performance
    .withColumn("quality_score", F.col("quality_pass_rate") * 100)
    .withColumn("consistency_score", F.least(F.col("quality_consistency") * 100, F.lit(100.0)))
    .withColumn("rework_score", F.greatest((1 - F.col("rework_rate")) * 100, F.lit(0.0)))
    .withColumn("efficiency_score", F.col("avg_process_efficiency") * 100)
    .withColumn("capacity_score", F.least(F.col("capacity_utilization") * 100, F.lit(100.0)))
    .withColumn(
        "acquisition_score",
        0.35 * F.col("quality_score")
        + 0.20 * F.col("consistency_score")
        + 0.15 * F.col("rework_score")
        + 0.15 * F.col("efficiency_score")
        + 0.15 * F.col("capacity_score")
    )
    .join(material_profiles, "plant_id", "left")
    .withColumn(
        "acquisition_priority",
        F.when(F.col("acquisition_score") >= 90, "High")
         .when(F.col("acquisition_score") >= 80, "Medium")
         .otherwise("Low")
    )
)

for name, df in {
    "plant_performance": plant_performance,
    "monthly_quality": monthly_quality,
    "acquisition_candidates": score,
}.items():
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(f"{GOLD_PATH}/{name}")
    )

print("Gold layer created successfully.")
