from pathlib import Path
import numpy as np
import pandas as pd

from config import OUTPUT_DIR, SEED


def generate_quality_tests(
    production: pd.DataFrame,
    output_dir: Path = OUTPUT_DIR,
) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 1)
    tier_adjustment = {
        "PLT001": 1.7, "PLT002": 0.2, "PLT003": 2.0, "PLT004": -0.8,
        "PLT005": 0.4, "PLT006": 1.4, "PLT007": -0.2, "PLT008": -0.7,
        "PLT009": 0.0, "PLT010": 2.2, "PLT011": -1.0, "PLT012": 1.2,
    }
    material_profile = pd.read_csv(output_dir / "plant_materials.csv")
    material_score = material_profile.groupby("plant_id")["quality_factor"].mean().to_dict()
    rows = []
    for i, row in production.reset_index(drop=True).iterrows():
        target = row["target_strength_mpa"]
        adjustment = tier_adjustment[row["plant_id"]]
        material_effect = (row["cement_kg_m3"] - 300) * 0.018
        moisture_effect = abs(row["moisture_pct"] - 4.5) * 0.65
        profile_effect = (material_score[row["plant_id"]] - 0.88) * 11
        noise = rng.normal(0, 2.1)
        strength_28d = target + adjustment + material_effect + profile_effect - moisture_effect + noise
        slump = float(np.clip(rng.normal(105, 18) + (row["moisture_pct"] - 4.5) * 5, 65, 160))
        air = float(np.clip(rng.normal(5.0, 0.8), 2.5, 7.5))
        density = float(np.clip(rng.normal(2350, 32), 2250, 2420))
        passed = strength_28d >= target * 0.90 and 70 <= slump <= 150 and 2.5 <= air <= 7.5
        rework = not passed
        rework_cost = row["material_cost_cad"] * (0.45 if rework else 0.0)
        rows.append({
            "quality_test_id": f"QTY{1000000 + i + 1}",
            "production_id": row["production_id"],
            "test_date": row["production_date"],
            "strength_28d_mpa": round(float(strength_28d), 2),
            "slump_mm": round(slump, 1),
            "air_content_pct": round(air, 2),
            "density_kg_m3": round(density, 1),
            "quality_pass": bool(passed),
            "rework_flag": bool(rework),
            "rework_cost_cad": round(float(rework_cost), 2),
        })
    df = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "quality_tests.csv", index=False)
    return df


if __name__ == "__main__":
    production_path = OUTPUT_DIR / "production.csv"
    materials_path = OUTPUT_DIR / "plant_materials.csv"
    if not production_path.exists() or not materials_path.exists():
        raise FileNotFoundError("Run data_simulation/run_all.py first.")
    production = pd.read_csv(production_path)
    df = generate_quality_tests(production)
    print(f"Generated {len(df):,} quality tests")
