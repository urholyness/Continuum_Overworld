#!/bin/bash

# Deployment script for Continuum Overworld Integration
# Usage: ./deploy-environment.sh <environment> [domain]

set -e

ENVIRONMENT=${1:-dev}
ROOT_DOMAIN=${2:-greenstemglobal.com}
STACK_NAME="cn-integration-${ENVIRONMENT}"
AWS_REGION=${AWS_REGION:-us-east-1}
TENANT_ID=${TENANT_ID:-org-main}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Continuum Overworld Integration${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Domain: ${ROOT_DOMAIN}${NC}"
echo -e "${BLUE}Stack: ${STACK_NAME}${NC}"
echo -e "${BLUE}Region: ${AWS_REGION}${NC}"

# Validate environment parameter
if [[ ! "$ENVIRONMENT" =~ ^(dev|stage|prod)$ ]]; then
    echo -e "${RED}❌ Error: Environment must be 'dev', 'stage', or 'prod'${NC}"
    exit 1
fi

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}" 
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq not found. Please install it first.${NC}"
    exit 1
fi

# Verify AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured or invalid.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build and deploy infrastructure
echo -e "\n${YELLOW}🏗️ Building SAM application...${NC}"
cd infra/aws

if ! sam build; then
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}🚀 Deploying infrastructure...${NC}"
if ! sam deploy \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        "Environment=${ENVIRONMENT}" \
        "DomainName=${ROOT_DOMAIN}" \
        "TenantId=${TENANT_ID}" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION" \
    --no-fail-on-empty-changeset; then
    echo -e "${RED}❌ Infrastructure deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"

# Get stack outputs
echo -e "\n${YELLOW}📋 Getting stack outputs...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

CLIENT_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

USER_POOL_DOMAIN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

echo -e "${GREEN}✅ Stack outputs retrieved${NC}"
echo -e "  API URL: ${API_URL}"
echo -e "  User Pool ID: ${USER_POOL_ID}"
echo -e "  Client ID: ${CLIENT_ID}"
echo -e "  Auth Domain: ${USER_POOL_DOMAIN}"

# Test API health
echo -e "\n${YELLOW}🏥 Testing API health...${NC}"
if curl -f "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ API health check failed - this may be temporary${NC}"
fi

# Seed data
echo -e "\n${YELLOW}🌱 Seeding data...${NC}"
cd ../../scripts

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing script dependencies...${NC}"
    npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb ts-node typescript > /dev/null 2>&1
fi

# Seed operational metrics
echo -e "${YELLOW}  - Seeding operational metrics...${NC}"
if ENVIRONMENT="$ENVIRONMENT" TENANT_ID="$TENANT_ID" npx ts-node seed-operational-metrics.ts > /dev/null 2>&1; then
    echo -e "${GREEN}    ✅ Operational metrics seeded${NC}"
else
    echo -e "${YELLOW}    ⚠️ Operational metrics seeding failed${NC}"
fi

# Seed trace events  
echo -e "${YELLOW}  - Seeding trace events...${NC}"
if ENVIRONMENT="$ENVIRONMENT" TENANT_ID="$TENANT_ID" npx ts-node seed-trace-events.ts > /dev/null 2>&1; then
    echo -e "${GREEN}    ✅ Trace events seeded${NC}"
else
    echo -e "${YELLOW}    ⚠️ Trace events seeding failed${NC}"
fi

# Seed farms
echo -e "${YELLOW}  - Seeding farms...${NC}"
if ENVIRONMENT="$ENVIRONMENT" TENANT_ID="$TENANT_ID" npx ts-node seed-farms.ts > /dev/null 2>&1; then
    echo -e "${GREEN}    ✅ Farms seeded${NC}"
else
    echo -e "${YELLOW}    ⚠️ Farms seeding failed${NC}"
fi

# Seed agents
echo -e "${YELLOW}  - Seeding agents...${NC}"
if ENVIRONMENT="$ENVIRONMENT" TENANT_ID="$TENANT_ID" npx ts-node seed-agents.ts > /dev/null 2>&1; then
    echo -e "${GREEN}    ✅ Agents seeded${NC}"
else
    echo -e "${YELLOW}    ⚠️ Agents seeding failed${NC}"
fi

# Create test users (DEV environment only)
if [ "$ENVIRONMENT" = "dev" ]; then
    echo -e "\n${YELLOW}👥 Creating test users...${NC}"
    
    # Create admin user
    if aws cognito-idp admin-create-user \
        --user-pool-id "$USER_POOL_ID" \
        --username admin@example.com \
        --user-attributes Name=email,Value=admin@example.com \
        --temporary-password TempPass123! \
        --message-action SUPPRESS \
        --region "$AWS_REGION" > /dev/null 2>&1; then
        
        aws cognito-idp admin-set-user-password \
            --user-pool-id "$USER_POOL_ID" \
            --username admin@example.com \
            --password AdminPass123! \
            --permanent \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        aws cognito-idp admin-add-user-to-group \
            --user-pool-id "$USER_POOL_ID" \
            --username admin@example.com \
            --group-name admin \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        echo -e "${GREEN}  ✅ Admin user created (admin@example.com / AdminPass123!)${NC}"
    else
        echo -e "${YELLOW}  ⚠️ Admin user already exists or creation failed${NC}"
    fi
    
    # Create ops user
    if aws cognito-idp admin-create-user \
        --user-pool-id "$USER_POOL_ID" \
        --username ops@example.com \
        --user-attributes Name=email,Value=ops@example.com \
        --temporary-password TempPass123! \
        --message-action SUPPRESS \
        --region "$AWS_REGION" > /dev/null 2>&1; then
        
        aws cognito-idp admin-set-user-password \
            --user-pool-id "$USER_POOL_ID" \
            --username ops@example.com \
            --password OpsPass123! \
            --permanent \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        aws cognito-idp admin-add-user-to-group \
            --user-pool-id "$USER_POOL_ID" \
            --username ops@example.com \
            --group-name ops \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        echo -e "${GREEN}  ✅ Ops user created (ops@example.com / OpsPass123!)${NC}"
    else
        echo -e "${YELLOW}  ⚠️ Ops user already exists or creation failed${NC}"
    fi
    
    # Create trace user
    if aws cognito-idp admin-create-user \
        --user-pool-id "$USER_POOL_ID" \
        --username trace@example.com \
        --user-attributes Name=email,Value=trace@example.com \
        --temporary-password TempPass123! \
        --message-action SUPPRESS \
        --region "$AWS_REGION" > /dev/null 2>&1; then
        
        aws cognito-idp admin-set-user-password \
            --user-pool-id "$USER_POOL_ID" \
            --username trace@example.com \
            --password TracePass123! \
            --permanent \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        aws cognito-idp admin-add-user-to-group \
            --user-pool-id "$USER_POOL_ID" \
            --username trace@example.com \
            --group-name trace \
            --region "$AWS_REGION" > /dev/null 2>&1
            
        echo -e "${GREEN}  ✅ Trace user created (trace@example.com / TracePass123!)${NC}"
    else
        echo -e "${YELLOW}  ⚠️ Trace user already exists or creation failed${NC}"
    fi
fi

# Run validation
echo -e "\n${YELLOW}✅ Running validation tests...${NC}"
cd ..

# Make sure validation script is executable
chmod +x scripts/validate-environment.sh

# Run basic validation (without JWT tokens)
if ./scripts/validate-environment.sh "$ENVIRONMENT" "$ROOT_DOMAIN"; then
    echo -e "${GREEN}✅ Basic validation passed${NC}"
else
    echo -e "${YELLOW}⚠️ Some validation tests failed - check logs above${NC}"
fi

# Display summary
echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}===================${NC}"
echo -e "Environment: ${ENVIRONMENT}"
echo -e "API URL: ${API_URL}"
echo -e "Auth Domain: ${USER_POOL_DOMAIN}"

if [ "$ENVIRONMENT" = "dev" ]; then
    echo -e "\n${BLUE}Test Users Created:${NC}"
    echo -e "  Admin: admin@example.com / AdminPass123!"
    echo -e "  Ops: ops@example.com / OpsPass123!"
    echo -e "  Trace: trace@example.com / TracePass123!"
fi

echo -e "\n${BLUE}Amplify Environment Variables:${NC}"
echo -e "NEXT_PUBLIC_SITE_ENV=${ENVIRONMENT}"
echo -e "NEXT_PUBLIC_API_BASE_URL=${API_URL}"
echo -e "AUTH_ISSUER=https://cognito-idp.${AWS_REGION}.amazonaws.com/${USER_POOL_ID}"
echo -e "AUTH_CLIENT_ID=${CLIENT_ID}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "1. Configure Amplify environment variables (above)"
echo -e "2. Deploy frontend applications"
echo -e "3. Run full contract tests with JWT tokens"
echo -e "4. Monitor CloudWatch metrics and alarms"

echo -e "\n${GREEN}✨ Ready for integration testing!${NC}"