from pyspark.sql import functions as F

SILVER_PATH = "dbfs:/FileStore/concrete_quality/silver"
GOLD_PATH = "dbfs:/FileStore/concrete_quality/gold"

plants = spark.read.format("delta").load(f"{SILVER_PATH}/plants")
performance = spark.read.format("delta").load(f"{GOLD_PATH}/plant_performance")
plant_materials = spark.read.format("delta").load(f"{SILVER_PATH}/plant_materials")

owned = (
    performance
    .join(plants.select("plant_id", "ownership_status"), "plant_id")
    .filter(F.col("ownership_status") == "Owned")
    .select(
        F.col("plant_id").alias("anchor_plant_id"),
        F.col("plant_name").alias("anchor_plant_name"),
        F.col("latitude").alias("anchor_lat"),
        F.col("longitude").alias("anchor_lon"),
        F.col("quality_pass_rate").alias("anchor_quality"),
    )
)

targets = (
    performance
    .join(plants.select("plant_id", "ownership_status"), "plant_id")
    .filter(F.col("ownership_status") == "Target")
    .select(
        F.col("plant_id").alias("target_plant_id"),
        F.col("plant_name").alias("target_plant_name"),
        F.col("latitude").alias("target_lat"),
        F.col("longitude").alias("target_lon"),
        F.col("quality_pass_rate").alias("target_quality"),
        F.col("rework_rate").alias("target_rework"),
        F.col("avg_process_efficiency").alias("target_efficiency"),
    )
)

# Haversine distance in km between an owned plant and a target plant.
lat1 = F.radians(F.col("anchor_lat"))
lat2 = F.radians(F.col("target_lat"))
dlat = lat2 - lat1
dlon = F.radians(F.col("target_lon")) - F.radians(F.col("anchor_lon"))
a = F.pow(F.sin(dlat / 2), 2) + F.cos(lat1) * F.cos(lat2) * F.pow(F.sin(dlon / 2), 2)
distance_km = 6371.0 * 2 * F.asin(F.sqrt(a))

pairs = owned.crossJoin(targets).withColumn("distance_km", distance_km)

owned_materials = (
    plant_materials
    .join(plants.select("plant_id", "ownership_status"), "plant_id")
    .filter(F.col("ownership_status") == "Owned")
    .select(
        F.col("plant_id").alias("anchor_plant_id"),
        F.col("material_group"),
        F.col("material_id").alias("anchor_material_id"),
    )
)

target_materials = (
    plant_materials
    .join(plants.select("plant_id", "ownership_status"), "plant_id")
    .filter(F.col("ownership_status") == "Target")
    .select(
        F.col("plant_id").alias("target_plant_id"),
        F.col("material_group"),
        F.col("material_id").alias("target_material_id"),
    )
)

material_matches = (
    owned_materials.join(target_materials, "material_group")
    .filter(F.col("anchor_material_id") == F.col("target_material_id"))
    .groupBy("anchor_plant_id", "target_plant_id")
    .agg(F.count("material_group").alias("matching_material_groups"))
)

result = (
    pairs.join(material_matches, ["anchor_plant_id", "target_plant_id"], "left")
    .fillna({"matching_material_groups": 0})
    .withColumn("material_similarity_pct", F.col("matching_material_groups") / F.lit(5.0) * 100)
    .withColumn("proximity_score", 100 * F.exp(-F.col("distance_km") / 100))
    .withColumn("quality_score", F.col("target_quality") * 100)
    .withColumn("rework_score", (1 - F.col("target_rework")) * 100)
    .withColumn("efficiency_score", F.col("target_efficiency") * 100)
    .withColumn(
        "acquisition_score",
        0.30 * F.col("quality_score")
        + 0.20 * F.col("material_similarity_pct")
        + 0.20 * F.col("proximity_score")
        + 0.15 * F.col("rework_score")
        + 0.15 * F.col("efficiency_score")
    )
    .withColumn(
        "recommendation",
        F.when(F.col("acquisition_score") >= 80, "Prioritize")
         .when(F.col("acquisition_score") >= 65, "Review")
         .otherwise("Deprioritize")
    )
)

result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
    f"{GOLD_PATH}/acquisition_pair_analysis"
)

print("Acquisition pair analysis created successfully.")

from pyspark.sql.window import Window

window = Window.partitionBy("target_plant_id").orderBy(F.desc("acquisition_score"))
summary = (
    result.withColumn("rank_within_target", F.row_number().over(window))
    .filter(F.col("rank_within_target") == 1)
    .drop("rank_within_target")
)
summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
    f"{GOLD_PATH}/acquisition_target_summary"
)
