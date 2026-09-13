from pathlib import Path
import numpy as np
import pandas as pd

from config import END_DATE, OUTPUT_DIR, PLANT_PROFILES, SEED, START_DATE


PRODUCTS = [
    ("C25", 25, 185.0),
    ("C30", 30, 198.0),
    ("C35", 35, 212.0),
    ("C40", 40, 228.0),
]


def generate_production(output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    rows = []
    production_id = 1

    for plant_idx, plant in enumerate(PLANT_PROFILES):
        plant_id = plant[0]
        tier = plant[-1]
        base_efficiency = {"A": 0.91, "B": 0.86, "C": 0.81}[tier]
        for date in dates:
            if date.weekday() >= 5 and rng.random() < 0.25:
                continue
            daily_batches = int(rng.integers(2, 6))
            for _ in range(daily_batches):
                product, target_strength, base_price = PRODUCTS[int(rng.integers(0, len(PRODUCTS)))]
                volume = float(np.clip(rng.normal(110, 22), 55, 180))
                cement = {"C25": 260, "C30": 300, "C35": 330, "C40": 365}[product]
                water = {"C25": 180, "C30": 175, "C35": 168, "C40": 160}[product]
                fine_agg = 760 + rng.normal(0, 25)
                coarse_agg = 1020 + rng.normal(0, 30)
                moisture = float(np.clip(rng.normal(4.5, 1.2), 1.5, 8.0))
                efficiency = float(np.clip(base_efficiency + rng.normal(0, 0.035), 0.70, 0.98))
                material_cost = volume * (base_price * (1.0 + (1.0 - efficiency) * 0.25))
                rows.append({
                    "production_id": f"PRD{production_id:07d}",
                    "plant_id": plant_id,
                    "production_date": date.date().isoformat(),
                    "product_code": product,
                    "target_strength_mpa": target_strength,
                    "volume_m3": round(volume, 2),
                    "cement_kg_m3": round(cement + rng.normal(0, 6), 2),
                    "water_l_m3": round(water + rng.normal(0, 4), 2),
                    "fine_aggregate_kg_m3": round(fine_agg, 2),
                    "coarse_aggregate_kg_m3": round(coarse_agg, 2),
                    "moisture_pct": round(moisture, 2),
                    "process_efficiency": round(efficiency, 4),
                    "material_cost_cad": round(material_cost, 2),
                })
                production_id += 1

    df = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "production.csv", index=False)
    return df


if __name__ == "__main__":
    df = generate_production()
    print(f"Generated {len(df):,} production batches")
