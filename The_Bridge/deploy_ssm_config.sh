#!/bin/bash
set -e

echo "🔧 Storing C_N Configuration in SSM Parameter Store..."

AWS_REGION=${AWS_REGION:-us-east-1}

# Core configuration (non-secret)
aws ssm put-parameter \
    --name "/C_N/Config/Environment" \
    --value "PROD" \
    --type String \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Config" \
    --overwrite \
    2>/dev/null && echo "  ✓ Environment config" || echo "  ✓ Environment exists"

aws ssm put-parameter \
    --name "/C_N/Config/Region" \
    --value "$AWS_REGION" \
    --type String \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Config" \
    --overwrite \
    2>/dev/null && echo "  ✓ Region config" || echo "  ✓ Region exists"

aws ssm put-parameter \
    --name "/C_N/Config/EventBus" \
    --value "C_N-EventBus-Core" \
    --type String \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Config" \
    --overwrite \
    2>/dev/null && echo "  ✓ EventBus config" || echo "  ✓ EventBus exists"

# Resource references
aws ssm put-parameter \
    --name "/C_N/Resources/FarmMetricsTable" \
    --value "C_N-FarmMetrics-Live" \
    --type String \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Resource" \
    --overwrite \
    2>/dev/null

aws ssm put-parameter \
    --name "/C_N/Resources/PantheonRegistry" \
    --value "C_N-Pantheon-Registry" \
    --type String \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Resource" \
    --overwrite \
    2>/dev/null

echo "✅ SSM parameters configured (use Secrets Manager for future secrets)"