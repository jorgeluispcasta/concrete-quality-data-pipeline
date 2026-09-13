import pandas as pd
from config import PLANT_PROFILES, OUTPUT_DIR


def generate_plants() -> pd.DataFrame:
    columns = [
        "plant_id", "plant_name", "region", "latitude", "longitude",
        "annual_capacity_m3", "plant_tier"
    ]
    df = pd.DataFrame(PLANT_PROFILES, columns=columns)
    df["active"] = True
    df["ownership_status"] = ["Owned" if i < 6 else "Target" for i in range(len(df))]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / "plants.csv", index=False)
    return df


if __name__ == "__main__":
    df = generate_plants()
    print(f"Generated {len(df)} plants")
