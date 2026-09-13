from pathlib import Path
import pandas as pd

from config import MATERIALS, OUTPUT_DIR, PLANT_PROFILES


PLANT_MATERIAL_MAP = {
    "PLT001": ["MAT001", "MAT004", "MAT007", "MAT010", "MAT012"],
    "PLT002": ["MAT002", "MAT005", "MAT009", "MAT011", "MAT012"],
    "PLT003": ["MAT001", "MAT004", "MAT008", "MAT010", "MAT012"],
    "PLT004": ["MAT003", "MAT006", "MAT009", "MAT011", "MAT013"],
    "PLT005": ["MAT002", "MAT005", "MAT007", "MAT010", "MAT012"],
    "PLT006": ["MAT001", "MAT004", "MAT008", "MAT010", "MAT013"],
    "PLT007": ["MAT002", "MAT005", "MAT009", "MAT011", "MAT012"],
    "PLT008": ["MAT003", "MAT006", "MAT008", "MAT011", "MAT013"],
    "PLT009": ["MAT002", "MAT005", "MAT009", "MAT010", "MAT012"],
    "PLT010": ["MAT001", "MAT004", "MAT007", "MAT010", "MAT012"],
    "PLT011": ["MAT003", "MAT006", "MAT009", "MAT011", "MAT013"],
    "PLT012": ["MAT001", "MAT004", "MAT008", "MAT010", "MAT013"],
}


def generate_plant_materials() -> pd.DataFrame:
    material_lookup = {row[0]: row for row in MATERIALS}
    rows = []
    groups = ["Cement", "Fine Aggregate", "Coarse Aggregate", "Clay", "Admixture"]
    for plant in PLANT_PROFILES:
        plant_id = plant[0]
        for group, material_id in zip(groups, PLANT_MATERIAL_MAP[plant_id]):
            material = material_lookup[material_id]
            rows.append({
                "plant_id": plant_id,
                "material_group": group,
                "material_id": material_id,
                "quality_factor": material[4],
            })
    df = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / "plant_materials.csv", index=False)
    return df


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_plant_materials()
    df.to_csv(OUTPUT_DIR / "plant_materials.csv", index=False)
    print(f"Generated {len(df)} plant-material assignments")
