#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION?}"

aws events put-events --region "$AWS_REGION" --entries '[
  {"Source":"sat_agent","DetailType":"NDVIUpdate",
   "Detail":"{\"farm_id\":\"2BH\",\"drop_pct\":20}","EventBusName":"default"}
]' >/dev/null && echo "✅ Test alert event sent"

