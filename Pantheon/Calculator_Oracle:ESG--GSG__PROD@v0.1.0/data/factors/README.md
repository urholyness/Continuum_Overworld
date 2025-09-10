# Emission Factors

This directory contains emission factors used by the ESG Calculator Oracle.

## DEFRA 2024 Factors

The system is seeded with simplified DEFRA 2024 UK Government GHG Conversion Factors:

- **Transport modes**: Truck, Air, Rail, Sea
- **TTW/WTT split**: Tank-to-Wheel and Well-to-Tank emissions
- **Radiative Forcing**: Air freight RF uplift factors
- **Electricity**: Grid average and renewable sources

## Factor Structure

Each factor includes:
- `co2e_per_unit`: Base emission factor (kgCO₂e per unit)
- `ttw_share`: Tank-to-Wheel percentage (0-1)
- `wtt_share`: Well-to-Tank percentage (0-1)  
- `rf_uplift`: Radiative Forcing multiplier for air freight
- `table_ref`: Reference to source methodology

## Data Sources

- **Primary**: UK Government GHG Conversion Factors 2024
- **URL**: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
- **Methodology**: Based on ISO 14083:2023 and GLEC Framework v3.0

## Integration

Factors are loaded via `factors_loader.py` during database initialization. Future versions will support:

- Excel import from full DEFRA dataset
- Carrier-specific primary data
- Regional factor variants
- Custom factor packs