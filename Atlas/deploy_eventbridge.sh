#!/bin/bash
set -e

echo "📡 Creating C_N EventBridge Infrastructure..."

AWS_REGION=${AWS_REGION:-eu-central-1}
ENV_SUFFIX="${ENVIRONMENT:-PROD}"
BUS_NAME="C_N-EventBus-Core-${ENV_SUFFIX}"

# Create custom event bus
aws events create-event-bus \
    --name "$BUS_NAME" \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=EventBus" "Key=Division,Value=Atlas" \
    2>/dev/null && echo "  ✓ Created $BUS_NAME" || echo "  ✓ $BUS_NAME exists"

# Create rules for agent orchestration
echo "  Creating orchestration rules..."

# Rule 1: Farm IoT Data -> Process Metrics
aws events put-rule \
    --name "C_N-FarmData-Processor-${ENV_SUFFIX}" \
    --event-bus-name "$BUS_NAME" \
    --event-pattern '{"source":["IoT.Farm"],"detail-type":["MetricsUpdate"]}' \
    --state ENABLED \
    --description "Process incoming farm IoT metrics" \
    2>/dev/null && echo "    ✓ FarmData-Processor rule" || echo "    ✓ FarmData-Processor exists"

# Rule 2: Satellite NDVI -> Update Dashboard
aws events put-rule \
    --name "C_N-Satellite-NDVI-${ENV_SUFFIX}" \
    --event-bus-name "$BUS_NAME" \
    --event-pattern '{"source":["Oracle.Satellite"],"detail-type":["NDVI.Processed"]}' \
    --state ENABLED \
    --description "Update dashboards with NDVI data" \
    2>/dev/null && echo "    ✓ Satellite-NDVI rule" || echo "    ✓ Satellite-NDVI exists"

# Rule 3: Blockchain Events -> Notify Investors
aws events put-rule \
    --name "C_N-Blockchain-Update-${ENV_SUFFIX}" \
    --event-bus-name "$BUS_NAME" \
    --event-pattern '{"source":["Ledger.Blockchain"],"detail-type":["Checkpoint.Emitted"]}' \
    --state ENABLED \
    --description "Notify on blockchain checkpoints" \
    2>/dev/null && echo "    ✓ Blockchain-Update rule" || echo "    ✓ Blockchain-Update exists"

# Rule 4: Error Handling -> Aegis Alert
aws events put-rule \
    --name "C_N-Error-Handler-${ENV_SUFFIX}" \
    --event-bus-name "$BUS_NAME" \
    --event-pattern '{"detail-type":["Error","Exception","Failure"]}' \
    --state ENABLED \
    --description "Route errors to Aegis monitoring" \
    2>/dev/null && echo "    ✓ Error-Handler rule" || echo "    ✓ Error-Handler exists"

echo "✅ EventBridge infrastructure created"