# Calculator_Oracle:ESG--GSG__PROD@v0.1.0

## Purpose
Compute shipment/batch emissions for GreenStemGlobal using ISO 14083 methodology and GLEC parameters for transport (TTW/WTT), classify to GHG Protocol scopes/categories, and generate CBAM-ready embedded-emissions snippets.

## Features
- ISO 14083-compliant transport chain GHG calculations
- GLEC Framework v3 (2024) implementation
- GHG Protocol Scope 3 Category 4/9 mapping
- DEFRA 2024 conversion factors
- CBAM-ready emission reporting
- TTW/WTT split for all transport modes
- Radiative Forcing (RF) uplift for air freight

## Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Testing**: pytest (backend), Jest (frontend)

## Quick Start

### Backend Setup
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python factors_loader.py  # Load DEFRA 2024 factors
uvicorn app:app --reload
```

### Frontend Setup
```bash
cd web
npm install
npm run dev
```

## API Endpoints

- `POST /batches` - Create batch
- `POST /batches/{id}/legs` - Add transport legs
- `POST /batches/{id}/hubs` - Add hub activities
- `POST /batches/{id}/calculate` - Calculate emissions
- `GET /batches/{id}/cbam-snippet` - Get CBAM-ready text

## Calculation Methodology

### ISO 14083 Compliance
- Tank-to-Wheel (TTW) and Well-to-Tank (WTT) emissions split
- Distance-based and fuel-based calculation methods
- Proper allocation methods per transport mode

### GLEC Framework
- Energy source considerations
- Load factor adjustments
- Backhaul optimization

### GHG Protocol
- Scope 1: Direct emissions (owned vehicles)
- Scope 2: Electricity (hubs, cold storage)
- Scope 3 Category 4: Upstream transportation
- Scope 3 Category 9: Downstream transportation

## References
- [ISO 14083:2023](https://www.iso.org/standard/78864.html)
- [GLEC Framework v3.0](https://www.smartfreightcentre.org/en/glec-framework/)
- [GHG Protocol Scope 3 Standard](https://ghgprotocol.org/standards/scope-3-standard)
- [UK Government GHG Conversion Factors 2024](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024)