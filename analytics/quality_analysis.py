from pathlib import Path
import pandas as pd


def plant_quality_summary(production: pd.DataFrame, quality: pd.DataFrame, plants: pd.DataFrame) -> pd.DataFrame:
    df = production.merge(quality, on="production_id", how="left")
    summary = (
        df.groupby("plant_id", as_index=False)
        .agg(
            production_batches=("production_id", "nunique"),
            total_volume_m3=("volume_m3", "sum"),
            avg_strength_mpa=("strength_28d_mpa", "mean"),
            strength_stddev_mpa=("strength_28d_mpa", "std"),
            quality_pass_rate=("quality_pass", "mean"),
            rework_rate=("rework_flag", "mean"),
            rework_cost_cad=("rework_cost_cad", "sum"),
            avg_process_efficiency=("process_efficiency", "mean"),
        )
        .merge(plants[["plant_id", "plant_name", "region", "annual_capacity_m3", "ownership_status"]], on="plant_id")
    )
    summary["capacity_utilization"] = summary["total_volume_m3"] / summary["annual_capacity_m3"]
    return summary.sort_values("quality_pass_rate", ascending=False)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    output = root / "data" / "analytics"
    output.mkdir(parents=True, exist_ok=True)
    plants = pd.read_csv(raw / "plants.csv")
    production = pd.read_csv(raw / "production.csv")
    quality = pd.read_csv(raw / "quality_tests.csv")
    summary = plant_quality_summary(production, quality, plants)
    summary.to_csv(output / "plant_quality_summary.csv", index=False)
    print(summary[["plant_id", "plant_name", "quality_pass_rate", "rework_rate"]].to_string(index=False))


if __name__ == "__main__":
    main()
