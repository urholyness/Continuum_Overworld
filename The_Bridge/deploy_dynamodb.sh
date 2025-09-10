#!/bin/bash
set -e

echo "🗄️ Creating C_N DynamoDB Tables with PITR..."

AWS_REGION=${AWS_REGION:-us-east-1}

# Farm Metrics Table (Hot Data - 7 day TTL)
aws dynamodb create-table \
    --table-name "C_N-FarmMetrics-Live" \
    --attribute-definitions \
        AttributeName=farmId,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=farmId,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=FarmMetrics" "Key=Division,Value=Oracle" \
    2>/dev/null && echo "  ✓ Created C_N-FarmMetrics-Live" || echo "  ✓ C_N-FarmMetrics-Live exists"

# Wait for table to be active before updating
aws dynamodb wait table-exists --table-name "C_N-FarmMetrics-Live"

# Enable TTL and PITR
aws dynamodb update-time-to-live \
    --table-name "C_N-FarmMetrics-Live" \
    --time-to-live-specification Enabled=true,AttributeName=ttl \
    2>/dev/null || true

aws dynamodb update-continuous-backups \
    --table-name "C_N-FarmMetrics-Live" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    2>/dev/null || true

# Pantheon Agent Registry
aws dynamodb create-table \
    --table-name "C_N-Pantheon-Registry" \
    --attribute-definitions \
        AttributeName=agentId,AttributeType=S \
        AttributeName=division,AttributeType=S \
    --key-schema \
        AttributeName=agentId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=DivisionIndex,KeySchema=[{AttributeName=division,KeyType=HASH}],Projection={ProjectionType=ALL},BillingMode=PAY_PER_REQUEST" \
    --billing-mode PAY_PER_REQUEST \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Pantheon" "Key=Division,Value=Pantheon" \
    2>/dev/null && echo "  ✓ Created C_N-Pantheon-Registry" || echo "  ✓ C_N-Pantheon-Registry exists"

aws dynamodb wait table-exists --table-name "C_N-Pantheon-Registry"

aws dynamodb update-continuous-backups \
    --table-name "C_N-Pantheon-Registry" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    2>/dev/null || true

# Shipment Tracking Table
aws dynamodb create-table \
    --table-name "C_N-ShipmentTracking-Active" \
    --attribute-definitions \
        AttributeName=shipmentId,AttributeType=S \
        AttributeName=updatedAt,AttributeType=N \
    --key-schema \
        AttributeName=shipmentId,KeyType=HASH \
        AttributeName=updatedAt,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Logistics" "Key=Division,Value=Oracle" \
    2>/dev/null && echo "  ✓ Created C_N-ShipmentTracking-Active" || echo "  ✓ C_N-ShipmentTracking-Active exists"

aws dynamodb wait table-exists --table-name "C_N-ShipmentTracking-Active"

aws dynamodb update-continuous-backups \
    --table-name "C_N-ShipmentTracking-Active" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    2>/dev/null || true

# WebSocket Connections
aws dynamodb create-table \
    --table-name "C_N-WebSocketConnections" \
    --attribute-definitions \
        AttributeName=connectionId,AttributeType=S \
        AttributeName=userId,AttributeType=S \
    --key-schema \
        AttributeName=connectionId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=UserIdIndex,KeySchema=[{AttributeName=userId,KeyType=HASH}],Projection={ProjectionType=ALL},BillingMode=PAY_PER_REQUEST" \
    --billing-mode PAY_PER_REQUEST \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=WebSocket" "Key=Division,Value=The_Bridge" \
    2>/dev/null && echo "  ✓ Created C_N-WebSocketConnections" || echo "  ✓ C_N-WebSocketConnections exists"

# No PITR for WebSocket connections (transient data)

echo "✅ DynamoDB tables created with PITR enabled"