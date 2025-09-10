#!/usr/bin/env bash
set -euo pipefail
: "${READINGS_TABLE?}"; : "${FARM_ID?}"; : "${AWS_REGION?}"

TODAY=$(date -u +"%Y-%m-%d")
OUT=$(aws dynamodb query \
  --region "$AWS_REGION" \
  --table-name "$READINGS_TABLE" \
  --key-condition-expression "pk = :pk" \
  --expression-attribute-values "{\":pk\":{\"S\":\"${FARM_ID}#${TODAY}\"}}" \
  --limit 5)

echo "$OUT" | jq -e '.Count >= 1' >/dev/null || { echo "❌ No readings found for ${FARM_ID} today"; exit 1; }
echo "✅ Dynamo readings exist for ${FARM_ID} today"




