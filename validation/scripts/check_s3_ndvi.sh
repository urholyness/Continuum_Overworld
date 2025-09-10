#!/usr/bin/env bash
set -euo pipefail
: "${CURATED_BUCKET?}"; : "${FARM_ID?}"; : "${FARM_DATE_UTC?}"; : "${AWS_REGION?}"

aws s3 ls "s3://${CURATED_BUCKET}/sat/${FARM_ID}/${FARM_DATE_UTC}/ndvi.png" --region "$AWS_REGION" >/dev/null \
  && echo "✅ NDVI tile present" || { echo "❌ NDVI tile missing"; exit 1; }




