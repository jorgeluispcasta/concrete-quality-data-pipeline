from pyspark.sql import functions as F

BRONZE_PATH = "dbfs:/FileStore/concrete_quality/bronze"
SILVER_PATH = "dbfs:/FileStore/concrete_quality/silver"

plants = spark.read.format("delta").load(f"{BRONZE_PATH}/plants")
materials = spark.read.format("delta").load(f"{BRONZE_PATH}/materials")
plant_materials = spark.read.format("delta").load(f"{BRONZE_PATH}/plant_materials")
production = spark.read.format("delta").load(f"{BRONZE_PATH}/production")
quality = spark.read.format("delta").load(f"{BRONZE_PATH}/quality_tests")

# Clean and standardize plant data.
plants_clean = (
    plants
    .dropDuplicates(["plant_id"])
    .withColumn("plant_name", F.trim("plant_name"))
    .withColumn("region", F.upper(F.trim("region")))
    .filter(F.col("active") == True)
)

# Standardize material master.
materials_clean = (
    materials
    .dropDuplicates(["material_id"])
    .withColumn("material_group", F.trim("material_group"))
    .withColumn("supplier", F.trim("supplier"))
    .withColumn("unit_cost", F.col("unit_cost").cast("double"))
)

plant_materials_clean = (
    plant_materials
    .dropDuplicates(["plant_id", "material_group"])
    .join(materials_clean.select("material_id", "material_name", "supplier"), "material_id", "left")
)

production_clean = (
    production
    .dropDuplicates(["production_id"])
    .withColumn("production_date", F.to_date("production_date"))
    .withColumn("volume_m3", F.col("volume_m3").cast("double"))
    .withColumn("process_efficiency", F.col("process_efficiency").cast("double"))
    .filter(F.col("volume_m3") > 0)
)

quality_clean = (
    quality
    .dropDuplicates(["quality_test_id"])
    .withColumn("test_date", F.to_date("test_date"))
    .withColumn("quality_pass", F.col("quality_pass").cast("boolean"))
    .withColumn("rework_flag", F.col("rework_flag").cast("boolean"))
)

# Join production and quality into the main operational dataset.
production_quality = (
    production_clean.alias("p")
    .join(quality_clean.alias("q"), F.col("p.production_id") == F.col("q.production_id"), "left")
    .select(
        "p.*",
        "q.quality_test_id",
        "q.test_date",
        "q.strength_28d_mpa",
        "q.slump_mm",
        "q.air_content_pct",
        "q.density_kg_m3",
        "q.quality_pass",
        "q.rework_flag",
        "q.rework_cost_cad",
    )
)

outputs = {
    "plants": plants_clean,
    "materials": materials_clean,
    "plant_materials": plant_materials_clean,
    "production_quality": production_quality,
}

for name, df in outputs.items():
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(f"{SILVER_PATH}/{name}")
    )

print("Silver layer created successfully.")
