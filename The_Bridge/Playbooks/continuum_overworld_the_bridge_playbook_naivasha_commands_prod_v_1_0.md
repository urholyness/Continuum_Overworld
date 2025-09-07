# The_Bridge / Playbook--NaivashaCommands__PROD@v1.0.0

**Owner:** Naivasha (Number_1)  |  **Risk Gate:** Aegis:T1  |  **SLA:** Immediate routing

---

## Purpose
Standardize how Naivasha issues system-level commands to Claude, Cursor, and other Continuum_Overworld agents. Ensures predictable execution, full audit trail, and compliance with STOP→FIX→TEST→DOC.

---

## Command Grammar

### Structure
```
[Target Agent]: [Action] — [Context/Scope]

Phase(s):
  STOP → Describe what must freeze, and why.
  FIX  → Specify exact changes (paths, code blocks, deletions, adds).
  TEST → Define tests to validate fix, both unit + integration.
  DOC  → State what files must be updated (STATUS.md, CHANGES.md, Incident IDs).

Severity: HIGH | MEDIUM | LOW
SLA: Timeline for completion (eg. 2h, 1d)
```

---

## Example

```
Claude: Remove legacy contract — Ledger/Contracts--SupplyChain__ETH@v0.1.0

Phase(s):
  STOP → Freeze Ledger/Contracts until issue resolved.
  FIX  → Delete SupplyChainRFP.sol + test suite.
  TEST → Verify hardhat test suite passes without contract.
  DOC  → Update STATUS.md + CHANGES.md. Link to INC-20250820-01.md.

Severity: HIGH
SLA: 1d
```

Cursor: Validate ESG pipeline — Forge/Weaver--ESG_KPI__PROD@v1.0.0

Phase(s):
  STOP → Lock pipeline until validation complete.
  FIX  → None, Cursor is validator only.
  TEST → Confirm pipeline can ingest Lufthansa 2023 ESG report via Rank pipeline.
  DOC  → Append validation results to .bridge/validation/report-2025-08-20.json.

Severity: MEDIUM
SLA: 3d
```

---

## Downgrade / Close Rules
- Severity HIGH → Only Aegis may downgrade after successful TEST.
- Severity MEDIUM/LOW → Cursor can downgrade after passing TEST.
- Closure requires STATUS.md + CHANGES.md update.
- Every incident must link to an Incident ID (INC-YYYYMMDD-XX).

---

## Notes
- Naivasha is the only human authority issuing these system commands.
- Claude executes (builder/engineer), Cursor validates (auditor/checker).
- Aegis oversees risk gates and vetoes unsafe changes.
- All commands + results are logged for provenance.

