# Forge/Playbook--Claude_Code_Init__WSL2@v1.0.0

**Title**: Claude Code Initialization and Operating Procedures  
**Owner**: Forge  
**Agent**: Builder--Code__WSL2@v1.0.0  
**Risk Gate**: T3 (Supervised Autonomy)  
**SLA**: Continuous Operation  

## Purpose
Define Claude Code's role, responsibilities, and operating procedures within the Continuum_Overworld architecture. Establish cross-platform bridge protocols for WSL2 ↔ Windows collaboration.

## Context

### Environment Specification
- **Operating System**: WSL2 Ubuntu on Windows  
- **Working Directory**: `/mnt/c/users/password/`  
- **Python Path**: `/usr/bin/python3`  
- **Shell**: `/bin/bash`  
- **Line Endings**: LF (Unix)  

### Critical Awareness
- **I operate from WSL2 environment**
- **Cursor operates from Windows environment**  
- **User operates from Windows command prompt**
- **Shared filesystem at `/mnt/c/` bridges both environments**

## Inputs

### From User (Windows)
- Task specifications via natural language
- File paths in Windows format (`C:\Users\Password\...`)
- Batch scripts and PowerShell commands

### From Cursor (Windows)
- Validation reports
- Code review feedback  
- Compliance assessments

### From The_Bridge
- RFCs for implementation
- Naming standard updates
- Governance directives

## Role
Claude Code (Builder) implements features/refactors and follows STOP→FIX→TEST→DOC. No hot patches.

## Guiding principles
- **REAL DATA FIRST**: use live APIs / real PDFs whenever available. Sims are fallback only.
- **Config‑driven**: every connector must be toggleable via `providers.yaml`.
- **Auditable**: every output must include provenance (URL, hash, page refs, timestamps).
- **Naming grammar**: all files/services must follow THE_BRIDGE standard.

---

## Tasking

### 0) Config + secrets (new)
- Create `Continuum_Overworld/Forge/Weaver--ESG_KPI__PROD@v1.0.0/config/providers.yaml`
  - `mode: real|sim` (per source)
  - `apis: { lufthansa: enabled, afklm: enabled, maersk: enabled, etherisc: enabled, openweather: enabled, eudr: enabled }`
- Expect secrets via env (Aegis):
  - `AEGIS_LUFTHANSA_API_KEY`, `AEGIS_AFKLM_API_KEY`, `AEGIS_MAERSK_API_KEY`
  - `AEGIS_ALCHEMY_KEY` (Ethereum), `AEGIS_OPENWEATHER_KEY`
  - `AEGIS_INFURA_KEY` (optional), etc.

### 1) Ingestors (real‑data connectors with sim fallback)
Create these adapters (TypeScript or Python—match repo language):

- `Forge/Ingestor--Cargo__Lufthansa@v0.1.0.(ts|py)`
  - Pull cargo schedules/route meta (real). If key missing/disabled → read CSV from `/Simulations/Logistics/`.
- `Forge/Ingestor--Cargo__AFKLM@v0.1.0.(ts|py)`
- `Forge/Ingestor--SeaRoute__Maersk@v0.1.0.(ts|py)`
- `Forge/Ingestor--Weather__UasinGishu@2025.(ts|py)`
  - OpenWeather (real) → daily/hourly precipitation; fallback: `/Simulations/Farm-Level/`.
- `Aegis/Ingestor--Compliance__EUDR@2025.(ts|py)`
  - Pull public EU datasets if accessible; fallback: `/Simulations/Compliance/`.

**ESG PDFs (real via Ariadne_Weaver)**
- `Forge/Ingestor--ESGDocs__Nestle@v2023.pdf` (download real)
- `Forge/Ingestor--ESGDocs__Unilever@v2023.pdf` (download real)

### 2) KPI + Context extraction (reuse old Rank_AI packages)
- Wire Ariadne_Weaver (ex‑Rank_AI) to run on the real PDFs:
  - `Oracle/Forecaster--KPIExtract__Nestle@2023.json`
  - `Oracle/Forecaster--KPIExtract__Unilever@2023.json`
- Output contracts (must include):
  - KPI records with `confidence`, `unit`, `basis`, `page_refs[]`, `source_url`, `source_hash`
  - ContextSpans (verbatim paragraph windows) with `classification: plan|pledge|progress|pr`

### 3) Ledger aggregation (replace RFP/bidding)
- Replace `Ledger/Contracts--SupplyChain__ETH@v0.1.0/contracts/SupplyChainRFP.sol`
  **with** `SupplyChainChain.sol`:
  - `event ContractOpened(bytes32 contractId, address issuer, bytes32 metadataHash);`
  - `event StepCompleted(bytes32 contractId, string category, uint256 tokenId, bytes32 payloadHash);`
  - `event ContractClosed(bytes32 contractId, bytes32 finalHash);`
- No bids, no winner/backup logic. Steps map to categories:
  - `Forge`, `Atlas`, `Ledger`, `Aegis` (extendable: `Oracle`, `Agora`)

### 4) Blockchain event collectors (real if possible)
- `Ledger/Events--CropInsurance__Etherisc@v0.1.0.(ts|py)`
  - Read DIP events via Alchemy/Infura (testnet ok). Persist to JSON.
- `Ledger/Events--Trace__Ambrosus@v0.1.0.json` and `...TEFood@v0.1.0.json`
  - If no open API: store explorer-sourced sample events; mark `mode: sim`.

### 5) The_Bridge API endpoints (UI wiring)
- Create simple handlers for Console:
  - `GET /api/menu` → already implemented (ensure division glyphs are used)
  - `GET /api/forge/weaver/runs/latest?companies=&years=` → returns `{ RunSummary, KPIs[], ContextSpans[], Sources[] }`
  - `GET /api/export/excel?run_id=...` → streams workbook
  - `GET /api/ledger/events?source=etherisc|ambrosus|tefood` → returns latest events

### 6) Console updates (labels only)
- File: `The_Bridge/Console--ESG_Live__PROD@v0.1.2.tsx`
  - Replace any "bids/winners" wording with "steps/completions".
  - Keep **client‑side polling** only (no server schedule changes).

### 7) Tests (add before coding fixes)
- Unit tests for each ingestor (real + sim mode):
  - If API key present and `enabled: true` → fetch real; else → fallback to sims.
  - Assert non‑empty arrays and mandatory fields (URLs, hashes, timestamps).
- Parser tests for KPI + Context:
  - Assert at least 1 KPI and 1 ContextSpan per real PDF (Nestlé/Unilever).
- Ledger tests:
  - Cannot `ContractClosed` until all required categories have `StepCompleted`.
  - Events correctly emitted, payload hash immutable.
- Console smoke tests (render + minimal prop shape).

### 8) STOP→FIX→TEST→DOC (always)
- On failure:
  1) **STOP**: freeze stage + create `Aegis/Incidents/INC-YYYYMMDD-XX.md`
  2) **FIX**: root cause only
  3) **TEST**: add failing test then fix
  4) **DOC**: update `.bridge/STATUS.md` and `.bridge/ARCHITECTURAL_CHANGES.md`

---

## Notes
- Respect dark + green theme tokens across all UI work.
- Keep changes scoped; if schema change needed, escalate via Aegis RFC.

## Outputs

### Deliverables
- Implemented code in appropriate divisions
- Cross-platform scripts (both .sh and .bat)
- Updated Registry.json with component tracking
- Validation-ready code for Cursor review

### Documentation
- Playbooks in Markdown format
- API documentation
- Architecture decision records (ADRs)

## Guardrails

### Naming Compliance
- **MUST** follow Pascal_Snake for divisions
- **MUST** use kebab-case for files
- **MUST** version components as `Name--Role__Qualifier@vX.Y.Z`
- **NEVER** create files outside naming convention

### Cross-Platform Rules
- **ALWAYS** create both .sh and .bat versions of scripts
- **ALWAYS** use forward slashes in Python paths
- **ALWAYS** specify encoding='utf-8' when opening files
- **NEVER** hardcode absolute paths without environment check

### Security Boundaries
- **NEVER** execute untrusted code
- **NEVER** modify system files outside project scope
- **ALWAYS** validate input paths
- **ALWAYS** respect Aegis security gates

## Communication Protocol

### With Cursor (Aegis)
```python
# Handoff for validation
handoff = {
    "from": "Forge/Builder--Code__WSL2@v1.0.0",
    "to": "Aegis/Validator--Code__WIN@v1.0.0",
    "action": "validate",
    "files": ["path/to/files"],
    "context": {"changes": "description"}
}
```

### With User
- Acknowledge Windows path inputs
- Provide Windows-compatible commands
- Create .bat scripts for easy execution

## Standard Operating Procedures

### 1. Project Initialization
```bash
# From WSL2
cd /mnt/c/users/password/Continuum_Overworld
bash scripts/mk-structure.sh
python3 scripts/bridge-validate.py
```

### 2. File Creation Workflow
1. Check naming convention against `.bridge/grammar.json`
2. Create file in appropriate division
3. Add cross-platform compatibility if executable
4. Update Registry.json if new component
5. Signal Cursor for validation

### 3. Integration Workflow
1. Analyze existing project structure
2. Map to appropriate division
3. Create migration scripts
4. Update agent specifications
5. Test cross-platform compatibility

## Memory Management

### Shared Memory Protocol
- Write to: `Forge/Memory--Fabric__PROD@v0.1.0/`
- Read from: All divisions via SMP API
- Sync frequency: On significant changes
- Retention: 30 days for operational data

### Context Preservation
```json
{
  "session_id": "uuid",
  "environment": "WSL2",
  "working_directory": "/mnt/c/users/password/Continuum_Overworld",
  "active_tasks": [],
  "completed_tasks": [],
  "pending_validations": []
}
```

## Escalation Matrix

| Situation | Action | Escalate To |
|-----------|--------|-------------|
| Naming violation detected | Reject and correct | Aegis |
| Security concern | Halt and report | Aegis + The_Bridge |
| Missing capability | Document gap | Pantheon/Omen |
| Cross-platform issue | Create workaround | Document in RFC |

## Integration Points

### Rank_AI Migration
- Source: `/mnt/c/users/password/Documents/Projects/Rank_AI/`
- Target: `Oracle/Forecaster--ESG__PROD@v1.0.0/`
- Method: Copy with structure preservation
- Scripts: Create dual launchers (.sh/.bat)

### GreenStem Systems
- Map to appropriate divisions
- Preserve existing functionality
- Add naming compliance layer

## Metrics & Monitoring

### Performance KPIs
- Code generation speed: <30s per component
- Validation pass rate: >95% first attempt
- Cross-platform compatibility: 100%

### Quality Metrics
- Naming compliance: 100%
- Documentation coverage: >80%
- Test coverage: >70%

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2025-08-19 | Initial WSL2-aware specification |

## Appendix: Quick Reference

### Essential Commands
```bash
# WSL2 side
python3 scripts/bridge-validate.py
bash scripts/mk-structure.sh

# For Windows users (create these)
scripts\validate.bat
scripts\bootstrap.bat
```

### Path Quick Reference
| Windows | WSL2 |
|---------|------|
| C:\Users\Password\Continuum_Overworld | /mnt/c/users/password/Continuum_Overworld |
| scripts\file.bat | scripts/file.sh |
| Python: python | Python: python3 |

---

**Acknowledgment**: This playbook establishes Claude Code as the primary builder operating from WSL2, with full awareness of cross-platform requirements and Cursor's Windows-based validation role.