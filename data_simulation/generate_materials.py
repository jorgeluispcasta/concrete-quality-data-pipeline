import pandas as pd
from config import MATERIALS, OUTPUT_DIR


def generate_materials() -> pd.DataFrame:
    columns = ["material_id", "material_group", "material_name", "supplier", "quality_factor", "unit_cost"]
    df = pd.DataFrame(MATERIALS, columns=columns)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / "materials.csv", index=False)
    return df


if __name__ == "__main__":
    df = generate_materials()
    print(f"Generated {len(df)} materials")
