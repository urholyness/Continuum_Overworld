# Manual Deployment Guide - Helios+Site Integration v1.1.0

## Prerequisites Installation

Since SAM CLI is not installed in the current environment, you'll need to install it first:

### Install SAM CLI
```bash
# For Ubuntu/WSL2
curl -Lo aws-sam-cli.zip https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli.zip -d sam-installation
sudo ./sam-installation/install
sam --version
```

### Install jq (if needed)
```bash
sudo apt-get update && sudo apt-get install -y jq
```

## Quick Deployment Commands

Once SAM CLI is installed, you can use the automated deployment script:

### Deploy DEV Environment
```bash
cd /mnt/c/users/password/continuum_Overworld
chmod +x scripts/deploy-environment.sh
./scripts/deploy-environment.sh dev greenstemglobal.com
```

### Deploy STAGE Environment  
```bash
./scripts/deploy-environment.sh stage greenstemglobal.com
```

### Deploy PROD Environment
```bash
./scripts/deploy-environment.sh prod greenstemglobal.com
```

## Manual Step-by-Step Deployment (DEV)

If you prefer manual deployment or need to troubleshoot:

### 1. Deploy Infrastructure
```bash
cd infra/aws

# Build SAM application
sam build

# Deploy to DEV
sam deploy \
  --stack-name cn-integration-dev \
  --parameter-overrides \
    Environment=dev \
    DomainName=greenstemglobal.com \
    TenantId=org-main \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --no-fail-on-empty-changeset
```

### 2. Get Stack Outputs
```bash
aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs' \
  --region us-east-1

# Extract specific values
API_URL=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text \
  --region us-east-1)

USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text \
  --region us-east-1)

CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name cn-integration-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text \
  --region us-east-1)
```

### 3. Seed Data
```bash
cd scripts

# Install dependencies
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb ts-node typescript

# Seed all data
ENVIRONMENT=dev TENANT_ID=org-main npx ts-node seed-operational-metrics.ts
ENVIRONMENT=dev TENANT_ID=org-main npx ts-node seed-trace-events.ts
ENVIRONMENT=dev TENANT_ID=org-main npx ts-node seed-farms.ts
ENVIRONMENT=dev TENANT_ID=org-main npx ts-node seed-agents.ts
```

### 4. Create Test Users (DEV only)
```bash
# Create admin user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  --region us-east-1

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --password AdminPass123! \
  --permanent \
  --region us-east-1

aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --group-name admin \
  --region us-east-1

# Create ops user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --user-attributes Name=email,Value=ops@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  --region us-east-1

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --password OpsPass123! \
  --permanent \
  --region us-east-1

aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username ops@example.com \
  --group-name ops \
  --region us-east-1

# Create trace user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --user-attributes Name=email,Value=trace@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  --region us-east-1

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --password TracePass123! \
  --permanent \
  --region us-east-1

aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username trace@example.com \
  --group-name trace \
  --region us-east-1
```

### 5. Validate Environment
```bash
cd ..
chmod +x scripts/validate-environment.sh
./scripts/validate-environment.sh dev greenstemglobal.com
```

## Amplify Configuration

### Helios Console Environment Variables
After infrastructure deployment, configure these in AWS Amplify Console:

**DEV Branch:**
```bash
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/$USER_POOL_ID
AUTH_CLIENT_ID=$CLIENT_ID
AUTH_AUDIENCE=$CLIENT_ID
JWT_SECRET=dev-jwt-secret-key
```

### Website Environment Variables  
**DEV Branch:**
```bash
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111
```

## Troubleshooting

### Check Lambda Function Logs
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/cn-
aws logs tail /aws/lambda/cn-composer-ops-metrics-dev --follow
```

### Verify DynamoDB Tables
```bash
aws dynamodb describe-table --table-name C_N-Metrics-Operational-dev
aws dynamodb scan --table-name C_N-Metrics-Operational-dev --max-items 5
```

### Test API Endpoints
```bash
# Health check
curl -f https://cn-dev-api.greenstemglobal.com/health

# Test with JWT (after getting tokens)
curl -H "Authorization: Bearer $ADMIN_JWT" \
  https://cn-dev-api.greenstemglobal.com/admin/farms
```

## Next Steps After Deployment

1. ✅ Infrastructure deployed and validated
2. ✅ Data seeded and verified
3. ✅ Test users created (DEV only)
4. 🔄 Configure Amplify environment variables
5. 🔄 Deploy frontend applications
6. 🔄 Run contract tests with JWT tokens
7. 🔄 Monitor CloudWatch metrics and alarms
8. 🔄 Deploy to STAGE environment
9. 🔄 Deploy to PROD environment

---

**Document Version**: 1.0  
**Environment**: Ready for deployment  
**AWS Account**: 086143043656  
**Region**: us-east-1