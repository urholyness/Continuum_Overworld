# Stockholm Migration Plan - DynamoDB eu-north-1

**Status**: Ready for execution (requires elevated IAM permissions)  
**Target Region**: eu-north-1 (Stockholm)  
**Source Region**: eu-central-1 (Frankfurt)  

## 🎯 Why Stockholm?
- **30% cheaper** than Frankfurt for DynamoDB
- **Better latency** for Nordic operations
- **Future-proof** for EU data regulations

## 📋 Migration Steps (Manual - IAM Limited)

### Step 1: Create Backups (Frankfurt)
```bash
aws dynamodb create-backup \
  --table-name C_N-FarmMetrics-Live-PROD \
  --backup-name migrate-to-stockholm-20250911 \
  --region eu-central-1

aws dynamodb create-backup \
  --table-name C_N-WebSocketConnections-PROD \
  --backup-name migrate-websocket-stockholm-20250911 \
  --region eu-central-1

aws dynamodb create-backup \
  --table-name C_N-ShipmentTracking-Active-PROD \
  --backup-name migrate-shipment-stockholm-20250911 \
  --region eu-central-1
```

### Step 2: Create Tables (Stockholm)
```bash
# Farm Metrics Table
aws dynamodb create-table \
  --region eu-north-1 \
  --table-name C_N-FarmMetrics-Live-PROD \
  --attribute-definitions \
    AttributeName=farmId,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=farmId,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --tags Key=Environment,Value=C_N Key=Component,Value=FarmMetrics Key=Division,Value=Oracle

# WebSocket Connections
aws dynamodb create-table \
  --region eu-north-1 \
  --table-name C_N-WebSocketConnections-PROD \
  --attribute-definitions \
    AttributeName=connectionId,AttributeType=S \
    AttributeName=userId,AttributeType=S \
  --key-schema \
    AttributeName=connectionId,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=UserIdIndex,KeySchema=[{AttributeName=userId,KeyType=HASH}],Projection={ProjectionType=ALL} \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Environment,Value=C_N Key=Component,Value=WebSocket Key=Division,Value=The_Bridge

# Shipment Tracking
aws dynamodb create-table \
  --region eu-north-1 \
  --table-name C_N-ShipmentTracking-Active-PROD \
  --attribute-definitions \
    AttributeName=shipmentId,AttributeType=S \
    AttributeName=updatedAt,AttributeType=N \
  --key-schema \
    AttributeName=shipmentId,KeyType=HASH \
    AttributeName=updatedAt,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Environment,Value=C_N Key=Component,Value=Logistics Key=Division,Value=Oracle
```

### Step 3: Enable TTL and PITR
```bash
# Enable TTL
aws dynamodb update-time-to-live \
  --region eu-north-1 \
  --table-name C_N-FarmMetrics-Live-PROD \
  --time-to-live-specification Enabled=true,AttributeName=ttl

# Enable Point-in-Time Recovery
aws dynamodb update-continuous-backups \
  --region eu-north-1 \
  --table-name C_N-FarmMetrics-Live-PROD \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Repeat for other tables...
```

### Step 4: Data Migration (if needed)
```bash
# Option A: Export/Import (for large datasets)
aws dynamodb export-table-to-point-in-time \
  --region eu-central-1 \
  --table-arn arn:aws:dynamodb:eu-central-1:086143043656:table/C_N-FarmMetrics-Live-PROD \
  --s3-bucket c-n-migration-temp \
  --s3-bucket-owner 086143043656

# Option B: Scan and Put (for small datasets)
# Use scripts/migrate-data.js
```

## 📊 Cost Impact

### Frankfurt (eu-central-1) Current:
- DynamoDB read/write: €0.284/€1.421 per million RCU/WCU
- Storage: €0.285 per GB-month

### Stockholm (eu-north-1) New:
- DynamoDB read/write: €0.199/€0.994 per million RCU/WCU  
- Storage: €0.199 per GB-month

**Estimated Savings**: ~30% reduction in DynamoDB costs

## 🔧 Code Updates Required

### API Routes:
- ✅ Updated to use `eu-north-1` as default region
- ✅ Environment variable support maintained

### Deployment Scripts:
- Update all deployment scripts in The_Bridge/, Oracle/, Atlas/
- Change region from `eu-central-1` to `eu-north-1`

### Amplify Environment Variables:
```
AWS_REGION=eu-north-1
AWS_DEFAULT_REGION=eu-north-1
```

## ⚠️ Migration Checklist

- [ ] Create Stockholm tables
- [ ] Migrate 2 Butterflies Homestead data
- [ ] Update Amplify environment variables
- [ ] Test API connectivity
- [ ] Update deployment scripts
- [ ] Verify all services work
- [ ] Clean up Frankfurt tables (after verification)

## 🎯 Success Criteria

- [ ] API routes return data from Stockholm
- [ ] All DynamoDB operations work in eu-north-1
- [ ] 30% cost reduction achieved
- [ ] No downtime during migration

**Estimated Migration Time**: 1 hour  
**Cost**: One-time setup, then permanent savings