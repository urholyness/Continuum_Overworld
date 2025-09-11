# Amplify Environment Variables - Production Configuration

**App ID**: dgcik29wowtkc  
**Environment**: main  
**Region**: eu-north-1 (Stockholm)

## 🔧 Environment Variables to Add in Amplify Console

### Core AWS Configuration
```
AWS_REGION=eu-north-1
AWS_DEFAULT_REGION=eu-north-1
```

### DynamoDB Tables (ACTUAL DEPLOYED NAMES)
```
DDB_METRICS_TABLE=C_N-FarmMetrics-Live-PROD
DDB_WEBSOCKET_TABLE=C_N-WebSocketConnections-PROD
DDB_SHIPMENT_TABLE=C_N-ShipmentTracking-Active-PROD
```

### Public Site Configuration
```
NEXT_PUBLIC_SITE_URL=https://main.d1o0v91pjtyjuc.amplifyapp.com
NEXT_PUBLIC_SITE_ENV=production
NEXT_PUBLIC_AWS_REGION=eu-north-1
```

## 📋 Manual Steps for Amplify Console

1. **Go to AWS Console > Amplify**
2. **Click app**: dgcik29wowtkc (SiteGreenStemGlobalP)
3. **Navigate**: App settings > Environment variables
4. **Click**: "Manage variables"
5. **Add each variable** using "Add variable" button
6. **Click**: "Save" when all are added
7. **Automatic redeploy** will trigger

## ✅ Table Verification

These tables were confirmed to exist in eu-north-1:
- ✅ C_N-FarmMetrics-Live-PROD (for farm data)
- ✅ C_N-WebSocketConnections-PROD (for real-time updates)  
- ✅ C_N-ShipmentTracking-Active-PROD (for logistics)

## 🌱 Real Farm Data Ready

**2 Butterflies Homestead**:
- Location: Eldoret, Kenya (0.5143, 35.2698)
- Owner: GSG-KE-UG
- Size: 9 acres
- Status: Ready for seeding to DynamoDB