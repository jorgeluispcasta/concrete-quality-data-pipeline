from pathlib import Path
import pandas as pd

from quality_analysis import plant_quality_summary


def calculate_operational_score(summary: pd.DataFrame) -> pd.DataFrame:
    result = summary.copy()
    result["quality_score"] = result["quality_pass_rate"] * 100
    consistency = 1 / (1 + result["strength_stddev_mpa"].fillna(99))
    result["consistency_score"] = (consistency * 100).clip(upper=100)
    result["rework_score"] = ((1 - result["rework_rate"]) * 100).clip(lower=0)
    result["efficiency_score"] = result["avg_process_efficiency"] * 100
    result["capacity_score"] = (result["capacity_utilization"] * 100).clip(upper=100)
    result["operational_score"] = (
        0.35 * result["quality_score"]
        + 0.20 * result["consistency_score"]
        + 0.15 * result["rework_score"]
        + 0.15 * result["efficiency_score"]
        + 0.15 * result["capacity_score"]
    )
    result["operational_priority"] = pd.cut(
        result["operational_score"],
        bins=[-float("inf"), 80, 90, float("inf")],
        labels=["Needs attention", "Monitor", "Strong"],
    )
    return result.sort_values("operational_score", ascending=False)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    output = root / "data" / "analytics"
    output.mkdir(parents=True, exist_ok=True)
    plants = pd.read_csv(raw / "plants.csv")
    production = pd.read_csv(raw / "production.csv")
    quality = pd.read_csv(raw / "quality_tests.csv")
    summary = plant_quality_summary(production, quality, plants)
    scored = calculate_operational_score(summary)
    scored.to_csv(output / "plant_performance.csv", index=False)
    print(scored[["plant_id", "plant_name", "operational_score", "operational_priority"]].to_string(index=False))


if __name__ == "__main__":
    main()
