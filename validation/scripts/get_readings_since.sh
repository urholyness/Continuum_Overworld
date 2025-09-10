#!/usr/bin/env bash
set -euo pipefail
: "${API_BASE?}"
SINCE=$(date -u -d "-7 days" +"%Y-%m-%dT%H:%M:%SZ")
curl -fsSL "${API_BASE}/farms/2BH/readings?since=${SINCE}" | jq -e 'length >= 1' >/dev/null \
  && echo "✅ Readings stream ok" || { echo "❌ No readings returned"; exit 1; }




