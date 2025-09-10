#!/usr/bin/env bash
set -euo pipefail
: "${API_BASE?}"

curl -fsSL "${API_BASE}/farms/2BH/summary" | tee /tmp/summary.json | jq -e '.last_ndvi and .freshness' >/dev/null \
  && echo "✅ Summary ok" || { echo "❌ Summary missing fields"; exit 1; }




