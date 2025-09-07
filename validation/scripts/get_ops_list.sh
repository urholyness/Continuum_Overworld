#!/usr/bin/env bash
set -euo pipefail
: "${API_BASE?}"

curl -fsSL "${API_BASE}/farms/2BH/ops?limit=10" | jq -e 'length >= 1' >/dev/null \
  && echo "✅ GET /ops ok" || { echo "❌ GET /ops failed"; exit 1; }

