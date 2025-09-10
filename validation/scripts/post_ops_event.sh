#!/usr/bin/env bash
set -euo pipefail
: "${API_BASE?}"; : "${ADMIN_JWT?}"

curl -fsSL -X POST "${API_BASE}/ops" \
  -H "Authorization: Bearer ${ADMIN_JWT}" \
  -H "Content-Type: application/json" \
  -d '{"type":"Irrigation","note":"QA test event from Cursor"}' \
  | jq -e '.ok == true' >/dev/null \
  && echo "✅ POST /ops ok" || { echo "❌ POST /ops failed"; exit 1; }




