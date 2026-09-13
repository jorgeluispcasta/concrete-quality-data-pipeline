from pathlib import Path

SEED = 42
N_PLANTS = 12
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw"

# Fictional plants. Coordinates are intentionally synthetic and are not tied to real facilities.
PLANT_PROFILES = [
    ("PLT001", "North Ridge", "North", 43.90, -81.20, 180000, "A"),
    ("PLT002", "West Valley", "West", 43.72, -81.65, 155000, "B"),
    ("PLT003", "Lakeside", "East", 43.62, -80.35, 210000, "A"),
    ("PLT004", "Pine Creek", "North", 44.08, -80.72, 135000, "C"),
    ("PLT005", "Maple Junction", "Central", 43.55, -80.10, 195000, "B"),
    ("PLT006", "Granite Point", "West", 43.82, -81.95, 165000, "A"),
    ("PLT007", "Cedar Valley", "Central", 43.38, -80.78, 175000, "B"),
    ("PLT008", "Riverbend", "East", 43.95, -79.95, 145000, "C"),
    ("PLT009", "Ironwood", "North", 44.22, -81.45, 120000, "B"),
    ("PLT010", "Southgate", "South", 43.15, -80.45, 225000, "A"),
    ("PLT011", "Oak Valley", "South", 43.28, -79.98, 190000, "C"),
    ("PLT012", "Bluewater", "East", 43.78, -79.55, 205000, "A"),
]

MATERIALS = [
    ("MAT001", "Cement", "Portland Type I", "CementCo A", 0.90, 145.0),
    ("MAT002", "Cement", "Portland Type II", "CementCo B", 0.86, 138.0),
    ("MAT003", "Cement", "Blended Cement", "CementCo C", 0.82, 130.0),
    ("MAT004", "Fine Aggregate", "Natural Sand A", "AggregateCo A", 0.92, 32.0),
    ("MAT005", "Fine Aggregate", "Natural Sand B", "AggregateCo B", 0.88, 29.0),
    ("MAT006", "Fine Aggregate", "Manufactured Sand", "AggregateCo C", 0.84, 36.0),
    ("MAT007", "Coarse Aggregate", "Gravel 10mm A", "AggregateCo A", 0.94, 28.0),
    ("MAT008", "Coarse Aggregate", "Gravel 20mm A", "AggregateCo A", 0.93, 26.0),
    ("MAT009", "Coarse Aggregate", "Gravel 20mm B", "AggregateCo B", 0.87, 24.0),
    ("MAT010", "Clay", "Low Plasticity Clay", "ClayCo A", 0.95, 18.0),
    ("MAT011", "Clay", "Medium Plasticity Clay", "ClayCo B", 0.78, 16.0),
    ("MAT012", "Admixture", "Water Reducer", "ChemCo A", 0.96, 2.8),
    ("MAT013", "Admixture", "Accelerator", "ChemCo B", 0.91, 3.6),
]
