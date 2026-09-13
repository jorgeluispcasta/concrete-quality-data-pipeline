from generate_materials import generate_materials
from generate_plants import generate_plants
from generate_production import generate_production
from generate_plant_materials import generate_plant_materials
from generate_quality_tests import generate_quality_tests
from config import OUTPUT_DIR


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    materials = generate_materials()
    plants = generate_plants()
    plant_materials = generate_plant_materials()
    production = generate_production()
    quality = generate_quality_tests(production)
    print(f"Materials: {len(materials):,}")
    print(f"Plants: {len(plants):,}")
    print(f"Plant-material assignments: {len(plant_materials):,}")
    print(f"Production batches: {len(production):,}")
    print(f"Quality tests: {len(quality):,}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
