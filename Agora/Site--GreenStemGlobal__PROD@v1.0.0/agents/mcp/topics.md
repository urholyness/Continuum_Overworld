# MCP Topics

## Topic: finance.ledger.v1
- pull_ledger_snapshot(range) → money‑flow JSON
- push_bank_event(payload) → normalize + emit on‑chain
- get_tx_detail(hash) → enrich with FX/vendor/invoice metadata

## Topic: ops.traceability.v1
- list_lots(range) → lot[]
- get_lot(id) → lot