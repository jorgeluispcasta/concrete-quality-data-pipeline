# Power BI Dashboard

The dashboard is designed around three questions:

1. How consistent is production quality across plants?
2. Where is rework creating avoidable cost?
3. Which target plants are the strongest acquisition candidates?

## Suggested pages

### 1. Executive Overview
- Total volume (m3)
- Quality pass rate
- Rework rate
- Rework cost (CAD)
- Average strength (MPa)
- Plant ranking by quality pass rate

### 2. Plant Performance
- Quality pass rate by plant
- Rework rate by plant
- Monthly quality trend
- Average strength vs. target strength
- Capacity utilization

### 3. Acquisition
- Acquisition score by target plant
- Distance from nearest owned plant
- Material similarity
- Target quality pass rate
- Recommendation: Prioritize / Review / Deprioritize

## Data model

Use the Snowflake analytics schema as the semantic-model source:

- `DIM_PLANT`
- `DIM_MATERIAL`
- `DIM_PLANT_MATERIAL`
- `FACT_PRODUCTION_QUALITY`
- `V_PLANT_PERFORMANCE`
- `V_MONTHLY_QUALITY`
- `V_ACQUISITION_CANDIDATES`
- `V_ACQUISITION_TARGET_SUMMARY`

The DAX measures used in the dashboard are in `measures.dax`.

The `.pbix` file is intentionally not included so the repository stays portable and does not contain environment-specific credentials or connection metadata.
