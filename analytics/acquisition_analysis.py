from pathlib import Path
import math
import pandas as pd

from plant_performance import calculate_operational_score
from quality_analysis import plant_quality_summary


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_acquisition_analysis(
    plants: pd.DataFrame,
    performance: pd.DataFrame,
    plant_materials: pd.DataFrame,
) -> pd.DataFrame:
    owned = plants[plants["ownership_status"] == "Owned"].copy()
    targets = plants[plants["ownership_status"] == "Target"].copy()
    perf_cols = ["plant_id", "quality_pass_rate", "rework_rate", "avg_process_efficiency"]
    perf = performance[perf_cols]
    owned = owned.merge(perf, on="plant_id")
    targets = targets.merge(perf, on="plant_id")

    material_sets = (
        plant_materials.groupby("plant_id")["material_id"]
        .apply(set)
        .to_dict()
    )

    rows = []
    for _, anchor in owned.iterrows():
        for _, target in targets.iterrows():
            distance = haversine_km(anchor.latitude, anchor.longitude, target.latitude, target.longitude)
            matches = len(material_sets[anchor.plant_id] & material_sets[target.plant_id])
            rows.append({
                "anchor_plant_id": anchor.plant_id,
                "anchor_plant_name": anchor.plant_name,
                "target_plant_id": target.plant_id,
                "target_plant_name": target.plant_name,
                "anchor_quality": anchor.quality_pass_rate,
                "target_quality": target.quality_pass_rate,
                "target_rework": target.rework_rate,
                "target_efficiency": target.avg_process_efficiency,
                "distance_km": distance,
                "matching_material_groups": matches,
            })

    result = pd.DataFrame(rows)
    result["material_similarity_pct"] = result["matching_material_groups"] / 5 * 100
    result["proximity_score"] = result["distance_km"].map(lambda x: 100 * math.exp(-x / 100))
    result["quality_score"] = result["target_quality"] * 100
    result["rework_score"] = (1 - result["target_rework"]) * 100
    result["efficiency_score"] = result["target_efficiency"] * 100
    result["acquisition_score"] = (
        0.30 * result["quality_score"]
        + 0.20 * result["material_similarity_pct"]
        + 0.20 * result["proximity_score"]
        + 0.15 * result["rework_score"]
        + 0.15 * result["efficiency_score"]
    )
    result["recommendation"] = pd.cut(
        result["acquisition_score"],
        bins=[-float("inf"), 65, 80, float("inf")],
        labels=["Deprioritize", "Review", "Prioritize"],
    )
    return result.sort_values("acquisition_score", ascending=False)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    output = root / "data" / "analytics"
    output.mkdir(parents=True, exist_ok=True)
    plants = pd.read_csv(raw / "plants.csv")
    materials = pd.read_csv(raw / "plant_materials.csv")
    production = pd.read_csv(raw / "production.csv")
    quality = pd.read_csv(raw / "quality_tests.csv")
    summary = plant_quality_summary(production, quality, plants)
    performance = calculate_operational_score(summary)
    result = build_acquisition_analysis(plants, performance, materials)
    result.to_csv(output / "acquisition_candidates.csv", index=False)
    summary = result.loc[result.groupby("target_plant_id")["acquisition_score"].idxmax()].copy()
    summary.to_csv(output / "acquisition_target_summary.csv", index=False)
    print(summary.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
