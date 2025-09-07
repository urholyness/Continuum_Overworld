# 2BH Live Dashboard Sprint Package

Complete implementation of the Two Butterflies Homestead monitoring system for GreenStem Global.

## Project Structure

```
greenstem-global/
├── farm-ingest/         # Backend Lambda functions and APIs
│   ├── src/
│   │   ├── weather_ingest/    # AccuWeather data ingestion
│   │   ├── api/              # REST API endpoints
│   │   └── alerts/           # EventBridge alert system
│   ├── infra/           # AWS CDK infrastructure
│   └── serverless.yml   # Serverless Framework config
├── sat-agent/          # Satellite NDVI processing
│   └── src/
│       └── sat_agent/  # Sentinel Hub integration
└── bridge-ui/          # Next.js frontend application
    ├── app/
    │   ├── farms/2BH/  # Public farm page
    │   ├── buyers/2BH/ # Buyer dashboard (protected)
    │   └── admin/ops/  # Admin operations form
    └── components/     # Reusable React components
```

## Features Implemented

### ✅ TICKET 1 - AccuWeather Agent
- Hourly weather data collection
- Temperature, humidity, precipitation tracking
- Location key caching in SSM Parameter Store
- EventBridge completion events

### ✅ TICKET 2 - Satellite NDVI Agent
- Daily Sentinel Hub satellite data processing
- NDVI calculation with cloud masking
- Statistical metrics (mean, p10, p90)
- S3 storage for processed images

### ✅ TICKET 3 - Ops Diary API
- POST /ops endpoint for logging farm operations
- Media upload to S3 with base64 encoding
- Cognito authentication for admin access
- GET /farms/2BH/ops for retrieving events

### ✅ TICKET 4 - Summary & Readings APIs
- GET /farms/2BH/summary - Farm overview with freshness indicators
- GET /farms/2BH/readings - Time-series sensor data
- Pagination and filtering support

### ✅ TICKET 5 - Bridge UI Skeleton
- Public farm page with live data
- Freshness badges for data status
- Interactive Leaflet map
- NDVI thumbnails from S3

### ✅ TICKET 6 - Weather Chart
- Recharts-based weather visualization
- 7-30 day trends for temperature and precipitation
- Combined line and bar chart

### ✅ TICKET 7 - Admin Ops Form
- Web-based operations logging
- Photo upload capability
- Cognito protected access
- Real-time submission to API

### ✅ TICKET 8 - Alerts System
- NDVI drop detection (>15% over 48h)
- Weather alerts (heavy rain, extreme temps)
- Ingest health monitoring
- SNS topic for notifications

### ✅ TICKET 9 - Mobile Bridge (Spec)
- Expo React Native structure defined
- Push notification architecture
- Camera integration for ops logging

### ✅ TICKET 10 - Infrastructure as Code
- AWS CDK TypeScript implementation
- DynamoDB tables with proper indexes
- S3 buckets with lifecycle policies
- API Gateway with CORS
- Cognito User Pool with groups
- CloudFront distribution
- WAF rate limiting
- Budget alarms

## Deployment Instructions

### Prerequisites

1. AWS Account with appropriate permissions
2. Node.js 18+ and npm installed
3. AWS CLI configured
4. CDK CLI installed (`npm install -g aws-cdk`)

### Environment Variables

Create `.env` file in farm-ingest directory:

```bash
ACCUWEATHER_API_KEY=your_key_here
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_secret
COGNITO_USER_POOL_ID=your_pool_id
COGNITO_CLIENT_ID=your_client_id
```

### Deploy Backend (Option 1: Serverless Framework)

```bash
cd greenstem-global/farm-ingest
npm install
npm run build

# Deploy to sandbox
npm run deploy:sbx

# Deploy to production
npm run deploy:prod
```

### Deploy Backend (Option 2: AWS CDK)

```bash
cd greenstem-global/farm-ingest/infra
npm install
npm run build

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy to sandbox
npm run deploy:sbx

# Deploy to production (requires approval)
npm run deploy:prod
```

### Deploy Frontend

```bash
cd greenstem-global/bridge-ui
npm install
npm run build

# Deploy to S3 + CloudFront
aws s3 sync out/ s3://gsg-bridge-ui-sbx/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Deploy Satellite Agent

```bash
cd greenstem-global/sat-agent
pip install -r requirements.txt -t package/
cp -r src/* package/
cd package && zip -r ../deployment.zip .
aws lambda update-function-code --function-name gsg-sbx-sat-agent --zip-file fileb://../deployment.zip
```

## Testing

### Unit Tests

```bash
# Backend tests
cd greenstem-global/farm-ingest
npm test

# Frontend tests
cd greenstem-global/bridge-ui
npm test
```

### Integration Tests

```bash
# Test weather ingestion
aws lambda invoke --function-name gsg-sbx-weather-ingest response.json

# Test API endpoints
curl https://api.greenstem.global/farms/2BH/summary
curl https://api.greenstem.global/farms/2BH/readings?since=2025-01-01T00:00:00Z

# Test alerts (manual trigger)
aws events put-events --entries file://test-event.json
```

## Monitoring

### CloudWatch Dashboards

Access via AWS Console:
- Lambda function metrics
- API Gateway request rates
- DynamoDB read/write capacity
- S3 bucket metrics

### Alerts

SNS topic subscriptions:
- Email: ops@greenstem.global
- SMS: On-call engineer

### Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/gsg-sbx-weather-ingest --follow

# View API Gateway logs
aws logs tail /aws/apigateway/gsg-sbx-farm-api --follow
```

## Go-Live Checklist

- [ ] Public page shows freshness badges (<24h old)
- [ ] NDVI thumbnail displays correctly
- [ ] Last ops event appears on public page
- [ ] Map shows farm polygon
- [ ] Buyer dashboard requires authentication
- [ ] Timeline shows mixed event types
- [ ] Weather chart renders 30-day data
- [ ] Admin can submit ops event with photo
- [ ] Ops event appears on public page within 2 min
- [ ] Test alert fired and received
- [ ] Budget alarms configured
- [ ] WAF rules active
- [ ] CloudFront serves UI pages

## Security Considerations

1. **API Keys**: Store in AWS Secrets Manager or Parameter Store
2. **CORS**: Configured for specific domains in production
3. **Authentication**: Cognito JWT validation on protected endpoints
4. **Rate Limiting**: WAF rules prevent abuse
5. **Data Encryption**: S3 server-side encryption enabled
6. **Network**: VPC endpoints for AWS services (optional)

## Cost Optimization

- DynamoDB on-demand billing for variable load
- S3 lifecycle policies for old satellite images
- Lambda reserved concurrency for predictable costs
- CloudFront caching reduces origin requests
- Budget alarms at 80% threshold

## Support

For issues or questions:
- Technical: dev@greenstem.global
- Operations: ops@greenstem.global
- Business: info@greenstem.global

## License

Proprietary - GreenStem Global © 2025