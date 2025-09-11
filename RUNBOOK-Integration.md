# Integration Runbook - Helios+Site v1.1.0

## 🚀 DEPLOYMENT GUIDE

### Prerequisites

- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Node.js 20.x installed
- jq (for JSON processing)
- Environment variables configured

### Environment Configuration

```bash
# Set environment
export ENVIRONMENT=dev  # or stage, prod
export ROOT_DOMAIN=greenstemglobal.com
export AWS_REGION=us-east-1
export TENANT_ID=org-main

# JWT Tokens (for testing)
export ADMIN_JWT="your-admin-jwt-token"
export OPS_JWT="your-ops-jwt-token" 
export TRACE_JWT="your-trace-jwt-token"
```

## Step 1: Deploy Infrastructure

### 1.1 Deploy SAM Stack

```bash
cd infra/aws

# Build the SAM application
sam build

# Deploy to DEV environment
sam deploy \
  --stack-name cn-integration-dev \
  --parameter-overrides \
    Environment=dev \
    DomainName=$ROOT_DOMAIN \
    TenantId=$TENANT_ID \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

# Get outputs
aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs' \
  --region $AWS_REGION
```

### 1.2 Verify Infrastructure

```bash
# Check API Gateway deployment
API_URL=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text \
  --region $AWS_REGION)

curl -f $API_URL/health
```

## Step 2: Seed Data

### 2.1 Install Dependencies

```bash
cd scripts
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb ts-node typescript
```

### 2.2 Run Seed Scripts

```bash
# Seed operational metrics (last 7 days)
ENVIRONMENT=dev npx ts-node seed-operational-metrics.ts

# Seed trace events (last 3 days, 500 events)
ENVIRONMENT=dev npx ts-node seed-trace-events.ts

# Seed farms (8 demo farms)
ENVIRONMENT=dev npx ts-node seed-farms.ts

# Seed agents (10 demo agents)
ENVIRONMENT=dev npx ts-node seed-agents.ts
```

### 2.3 Verify Data

```bash
# Check data was seeded
aws dynamodb scan --table-name C_N-Metrics-Operational-dev --max-items 5
aws dynamodb scan --table-name C_N-Events-Trace-dev --max-items 5  
aws dynamodb scan --table-name C_N-Registry-Farms-dev --max-items 5
aws dynamodb scan --table-name C_N-Pantheon-Registry-dev --max-items 5
```

## Step 3: Configure Cognito

### 3.1 Create Test Users

```bash
# Get Cognito details from stack outputs
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text \
  --region $AWS_REGION)

CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text \
  --region $AWS_REGION)

# Create admin user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Add to admin group
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --group-name admin

# Create ops user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --user-attributes Name=email,Value=ops@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Add to ops group
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --group-name ops

# Create trace user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --user-attributes Name=email,Value=trace@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Add to trace group  
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --group-name trace
```

### 3.2 Set Permanent Passwords

```bash
# Set permanent passwords (users will need to change on first login)
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --password AdminPass123! \
  --permanent

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --password OpsPass123! \
  --permanent

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --password TracePass123! \
  --permanent
```

## Step 4: Run Validation Tests

### 4.1 Environment Validation

```bash
# Run full environment validation
./scripts/validate-environment.sh dev greenstemglobal.com
```

### 4.2 Contract Tests

```bash
cd tests/contract

# Install dependencies
npm install node-fetch @types/node

# Run contract tests
ENVIRONMENT=dev \
API_BASE_URL=https://cn-dev-api.greenstemglobal.com \
ADMIN_JWT=$ADMIN_JWT \
OPS_JWT=$OPS_JWT \
TRACE_JWT=$TRACE_JWT \
npx ts-node api-contract-tests.ts
```

## Step 5: Configure Amplify Applications

### 5.1 Helios Console Environment Variables

Navigate to AWS Amplify Console and configure environment variables for each branch:

**DEV Branch:**
```bash
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com  
NEXT_PUBLIC_WS_URL=wss://ws-dev.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/$USER_POOL_ID
AUTH_CLIENT_ID=$CLIENT_ID
AUTH_AUDIENCE=$CLIENT_ID
JWT_SECRET=dev-jwt-secret-key
```

### 5.2 Website Environment Variables

**DEV Branch:**
```bash
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111
```

## Step 6: Promote to STAGE/PROD

### 6.1 Deploy STAGE Environment

```bash
# Deploy infrastructure to STAGE
sam deploy \
  --stack-name cn-integration-stage \
  --parameter-overrides \
    Environment=stage \
    DomainName=$ROOT_DOMAIN \
    TenantId=$TENANT_ID \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

# Seed STAGE data
ENVIRONMENT=stage npx ts-node scripts/seed-operational-metrics.ts
ENVIRONMENT=stage npx ts-node scripts/seed-trace-events.ts  
ENVIRONMENT=stage npx ts-node scripts/seed-farms.ts
ENVIRONMENT=stage npx ts-node scripts/seed-agents.ts

# Validate STAGE
./scripts/validate-environment.sh stage greenstemglobal.com
```

### 6.2 Deploy PROD Environment

```bash
# Deploy infrastructure to PROD
sam deploy \
  --stack-name cn-integration-prod \
  --parameter-overrides \
    Environment=prod \
    DomainName=$ROOT_DOMAIN \
    TenantId=$TENANT_ID \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

# Seed PROD data
ENVIRONMENT=prod npx ts-node scripts/seed-operational-metrics.ts
ENVIRONMENT=prod npx ts-node scripts/seed-trace-events.ts
ENVIRONMENT=prod npx ts-node scripts/seed-farms.ts  
ENVIRONMENT=prod npx ts-node scripts/seed-agents.ts

# Validate PROD
./scripts/validate-environment.sh prod greenstemglobal.com
```

## 🔧 TROUBLESHOOTING

### Common Issues

1. **Lambda Function Errors**
   ```bash
   # Check function logs
   aws logs describe-log-groups --log-group-name-prefix /aws/lambda/cn-
   aws logs tail /aws/lambda/cn-composer-ops-metrics-dev --follow
   ```

2. **DynamoDB Access Issues**
   ```bash
   # Verify table exists
   aws dynamodb describe-table --table-name C_N-Metrics-Operational-dev
   
   # Check IAM permissions
   aws sts get-caller-identity
   ```

3. **API Gateway Issues**
   ```bash
   # Test endpoint directly
   aws apigatewayv2 get-apis
   aws apigatewayv2 get-routes --api-id YOUR_API_ID
   ```

4. **Cognito Authentication Issues**
   ```bash
   # Verify user pool configuration
   aws cognito-idp describe-user-pool --user-pool-id $USER_POOL_ID
   
   # Check user status
   aws cognito-idp admin-get-user --user-pool-id $USER_POOL_ID --username admin@example.com
   ```

### Performance Monitoring

```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=cn-composer-ops-metrics-dev \
  --statistics Average,Maximum \
  --start-time 2023-09-09T00:00:00Z \
  --end-time 2023-09-09T23:59:59Z \
  --period 3600
```

### Cost Monitoring

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2023-09-01,End=2023-09-30 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## 🚨 ROLLBACK PROCEDURES

### Emergency Rollback

1. **API Gateway Rollback**
   ```bash
   # Revert to previous deployment
   aws apigatewayv2 update-stage \
     --api-id $API_ID \
     --stage-name $ENVIRONMENT \
     --deployment-id $PREVIOUS_DEPLOYMENT_ID
   ```

2. **Lambda Function Rollback**
   ```bash
   # Update function to previous version
   aws lambda update-function-configuration \
     --function-name cn-composer-ops-metrics-dev \
     --environment Variables='{ROLLBACK=true}'
   ```

3. **Database Rollback**
   ```bash
   # Point-in-time recovery (if needed)
   aws dynamodb restore-table-to-point-in-time \
     --source-table-name C_N-Metrics-Operational-dev \
     --target-table-name C_N-Metrics-Operational-dev-backup \
     --restore-date-time 2023-09-09T10:00:00Z
   ```

## 📊 MONITORING DASHBOARD

### Key Metrics to Monitor

- **API Response Time**: < 600ms P95
- **Error Rate**: < 0.5%  
- **DynamoDB Throttling**: 0 events
- **Lambda Cold Starts**: < 10%
- **Cost Trending**: Within $75-90/month budget

### Alerts Configuration

```bash
# Create CloudWatch alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name "CN-API-HighErrorRate-${ENVIRONMENT}" \
  --alarm-description "API error rate above threshold" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

---

**Document Version**: 1.0  
**Last Updated**: September 2025  
**Environment**: DEV/STAGE/PROD  
**Next Review**: Monthly