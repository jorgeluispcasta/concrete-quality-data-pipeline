import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analytics"))

from acquisition_analysis import build_acquisition_analysis, haversine_km
from plant_performance import calculate_operational_score


def test_haversine_same_point_is_zero():
    assert haversine_km(43.0, -80.0, 43.0, -80.0) == 0


def test_operational_score_is_ordered():
    df = pd.DataFrame({
        "plant_id": ["A", "B"],
        "quality_pass_rate": [0.98, 0.85],
        "strength_stddev_mpa": [1.0, 4.0],
        "rework_rate": [0.02, 0.10],
        "avg_process_efficiency": [0.95, 0.80],
        "capacity_utilization": [0.75, 0.75],
    })
    scored = calculate_operational_score(df)
    assert scored.iloc[0]["plant_id"] == "A"
    assert scored.iloc[0]["operational_score"] > scored.iloc[1]["operational_score"]


def test_acquisition_analysis_returns_all_pairs():
    plants = pd.DataFrame({
        "plant_id": ["O1", "O2", "T1"],
        "plant_name": ["Owned 1", "Owned 2", "Target 1"],
        "ownership_status": ["Owned", "Owned", "Target"],
        "latitude": [43.0, 43.5, 43.1],
        "longitude": [-80.0, -80.5, -80.1],
    })
    performance = pd.DataFrame({
        "plant_id": ["O1", "O2", "T1"],
        "quality_pass_rate": [0.95, 0.90, 0.94],
        "rework_rate": [0.03, 0.05, 0.04],
        "avg_process_efficiency": [0.92, 0.88, 0.91],
    })
    materials = pd.DataFrame({
        "plant_id": ["O1", "O1", "O2", "T1", "T1"],
        "material_id": ["M1", "M2", "M3", "M1", "M2"],
    })
    result = build_acquisition_analysis(plants, performance, materials)
    assert len(result) == 2
    assert result["target_plant_id"].eq("T1").all()
    assert result["matching_material_groups"].max() == 2
