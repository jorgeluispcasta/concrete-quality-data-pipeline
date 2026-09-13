import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data_simulation"))

from generate_materials import generate_materials
from generate_plants import generate_plants
from generate_plant_materials import generate_plant_materials
from generate_production import generate_production
from generate_quality_tests import generate_quality_tests


def test_reference_data_shapes():
    assert len(generate_plants()) == 12
    assert len(generate_materials()) == 13
    assert len(generate_plant_materials()) == 60


def test_production_is_positive(tmp_path):
    df = generate_production(tmp_path)
    assert len(df) > 10000
    assert (df["volume_m3"] > 0).all()
    assert df["production_id"].is_unique


def test_quality_has_one_test_per_batch(tmp_path):
    plant_materials = generate_plant_materials()
    # The helper writes to the configured output directory; use the project raw folder here.
    production = generate_production()
    quality = generate_quality_tests(production)
    assert len(quality) == len(production)
    assert quality["quality_test_id"].is_unique
    assert quality["production_id"].is_unique
    assert quality["rework_flag"].isin([True, False]).all()
