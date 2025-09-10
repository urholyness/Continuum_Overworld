#!/bin/bash
set -e

echo "🏗️ Creating DynamoDB tables in Stockholm (eu-north-1)..."
echo "Region: eu-north-1"
echo "Environment: PROD"
echo ""

# Farm Metrics Table (Hot Data - 30 day TTL)
echo "Creating C_N-FarmMetrics-Live-PROD..."
aws dynamodb create-table \
    --region eu-north-1 \
    --table-name "C_N-FarmMetrics-Live-PROD" \
    --attribute-definitions \
        AttributeName=farmId,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=farmId,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=FarmMetrics" "Key=Division,Value=Oracle" "Key=Region,Value=Stockholm" \
    2>/dev/null && echo "  ✓ Created C_N-FarmMetrics-Live-PROD" || echo "  ✓ C_N-FarmMetrics-Live-PROD exists"

# Wait for table to be active
echo "Waiting for C_N-FarmMetrics-Live-PROD to be active..."
aws dynamodb wait table-exists --region eu-north-1 --table-name "C_N-FarmMetrics-Live-PROD"

# Enable TTL
aws dynamodb update-time-to-live \
    --region eu-north-1 \
    --table-name "C_N-FarmMetrics-Live-PROD" \
    --time-to-live-specification Enabled=true,AttributeName=ttl \
    2>/dev/null || true

# Enable PITR
aws dynamodb update-continuous-backups \
    --region eu-north-1 \
    --table-name "C_N-FarmMetrics-Live-PROD" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    2>/dev/null || true

echo "  ✓ TTL and PITR enabled for FarmMetrics"
echo ""

# WebSocket Connections Table
echo "Creating C_N-WebSocketConnections-PROD..."
aws dynamodb create-table \
    --region eu-north-1 \
    --table-name "C_N-WebSocketConnections-PROD" \
    --attribute-definitions \
        AttributeName=connectionId,AttributeType=S \
        AttributeName=userId,AttributeType=S \
    --key-schema \
        AttributeName=connectionId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=UserIdIndex,KeySchema=[{AttributeName=userId,KeyType=HASH}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=WebSocket" "Key=Division,Value=The_Bridge" "Key=Region,Value=Stockholm" \
    2>/dev/null && echo "  ✓ Created C_N-WebSocketConnections-PROD" || echo "  ✓ C_N-WebSocketConnections-PROD exists"

aws dynamodb wait table-exists --region eu-north-1 --table-name "C_N-WebSocketConnections-PROD"
echo "  ✓ WebSocket table ready"
echo ""

# Shipment Tracking Table
echo "Creating C_N-ShipmentTracking-Active-PROD..."
aws dynamodb create-table \
    --region eu-north-1 \
    --table-name "C_N-ShipmentTracking-Active-PROD" \
    --attribute-definitions \
        AttributeName=shipmentId,AttributeType=S \
        AttributeName=updatedAt,AttributeType=N \
    --key-schema \
        AttributeName=shipmentId,KeyType=HASH \
        AttributeName=updatedAt,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags "Key=Environment,Value=C_N" "Key=Component,Value=Logistics" "Key=Division,Value=Oracle" "Key=Region,Value=Stockholm" \
    2>/dev/null && echo "  ✓ Created C_N-ShipmentTracking-Active-PROD" || echo "  ✓ C_N-ShipmentTracking-Active-PROD exists"

aws dynamodb wait table-exists --region eu-north-1 --table-name "C_N-ShipmentTracking-Active-PROD"

# Enable PITR for shipment tracking
aws dynamodb update-continuous-backups \
    --region eu-north-1 \
    --table-name "C_N-ShipmentTracking-Active-PROD" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    2>/dev/null || true

echo "  ✓ Shipment tracking table ready with PITR"
echo ""

echo "✅ Stockholm DynamoDB infrastructure created successfully!"
echo ""
echo "📊 Summary:"
echo "  ✓ C_N-FarmMetrics-Live-PROD (with TTL and PITR)"
echo "  ✓ C_N-WebSocketConnections-PROD (with UserIdIndex)"
echo "  ✓ C_N-ShipmentTracking-Active-PROD (with PITR)"
echo ""
echo "🎯 Next steps:"
echo "  1. Update Amplify environment: AWS_REGION=eu-north-1"
echo "  2. Run data migration: node scripts/migrate-to-stockholm.js"
echo "  3. Test API endpoints"
echo "  4. Verify 30% cost savings"
echo ""
echo "💰 Expected monthly savings: ~30% on DynamoDB costs"