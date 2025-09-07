#!/bin/bash

# Setup secrets management for Continuum_Overworld
set -e

ENVIRONMENT=${1:-staging}
REGION=${AWS_REGION:-us-east-1}

echo "🔐 Setting up secrets management for $ENVIRONMENT environment..."

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region $REGION >/dev/null 2>&1; then
        aws secretsmanager update-secret \
            --secret-id "$secret_name" \
            --secret-string "$secret_value" \
            --region $REGION
        echo "✅ Updated secret: $secret_name"
    else
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --description "$description" \
            --secret-string "$secret_value" \
            --region $REGION
        echo "✅ Created secret: $secret_name"
    fi
}

# Create AWS Cognito User Pool for investor authentication
echo "👤 Creating Cognito User Pool..."
USER_POOL_ID=$(aws cognito-idp create-user-pool \
    --pool-name "continuum-investors-$ENVIRONMENT" \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": false
        }
    }' \
    --auto-verified-attributes email \
    --username-attributes email \
    --region $REGION \
    --query 'UserPool.Id' \
    --output text 2>/dev/null || aws cognito-idp list-user-pools --max-items 60 --region $REGION --query "UserPools[?Name=='continuum-investors-$ENVIRONMENT'].Id" --output text)

# Create Cognito App Client
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
    --user-pool-id $USER_POOL_ID \
    --client-name "greenstem-website-$ENVIRONMENT" \
    --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH \
    --prevent-user-existence-errors ENABLED \
    --region $REGION \
    --query 'UserPoolClient.ClientId' \
    --output text 2>/dev/null || aws cognito-idp list-user-pool-clients --user-pool-id $USER_POOL_ID --region $REGION --query "UserPoolClients[?ClientName=='greenstem-website-$ENVIRONMENT'].ClientId" --output text)

# Store Cognito configuration
create_or_update_secret "continuum/$ENVIRONMENT/cognito" \
    "{\"user_pool_id\":\"$USER_POOL_ID\",\"client_id\":\"$CLIENT_ID\"}" \
    "Cognito configuration for Continuum_Overworld $ENVIRONMENT"

# Create API keys for external services (placeholders)
create_or_update_secret "continuum/$ENVIRONMENT/api-keys" \
    "{
        \"accuweather_api_key\":\"YOUR_ACCUWEATHER_KEY\",
        \"sentinelhub_client_id\":\"YOUR_SENTINELHUB_CLIENT_ID\",
        \"sentinelhub_client_secret\":\"YOUR_SENTINELHUB_SECRET\",
        \"openai_api_key\":\"YOUR_OPENAI_KEY\",
        \"claude_api_key\":\"YOUR_CLAUDE_KEY\"
    }" \
    "External API keys for Continuum_Overworld $ENVIRONMENT"

# Create blockchain configuration
create_or_update_secret "continuum/$ENVIRONMENT/blockchain" \
    "{
        \"network\":\"sepolia\",
        \"chain_id\":11155111,
        \"rpc_url\":\"https://sepolia.infura.io/v3/YOUR_PROJECT_ID\",
        \"contract_address\":\"WILL_BE_SET_AFTER_DEPLOYMENT\"
    }" \
    "Blockchain configuration for Continuum_Overworld $ENVIRONMENT"

# Create S3 configuration
create_or_update_secret "continuum/$ENVIRONMENT/storage" \
    "{
        \"bucket_data_lake\":\"continuum-overworld-lake-$ENVIRONMENT\",
        \"bucket_assets\":\"greenstem-global-assets-$ENVIRONMENT\",
        \"bucket_backups\":\"continuum-overworld-backups-$ENVIRONMENT\"
    }" \
    "Storage configuration for Continuum_Overworld $ENVIRONMENT"

# Create application secrets
APP_SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)

create_or_update_secret "continuum/$ENVIRONMENT/app" \
    "{
        \"secret_key\":\"$APP_SECRET_KEY\",
        \"jwt_secret\":\"$JWT_SECRET\",
        \"debug\":$([ "$ENVIRONMENT" = "production" ] && echo "false" || echo "true")
    }" \
    "Application secrets for Continuum_Overworld $ENVIRONMENT"

# Create monitoring configuration
create_or_update_secret "continuum/$ENVIRONMENT/monitoring" \
    "{
        \"slack_webhook\":\"YOUR_SLACK_WEBHOOK\",
        \"email_alerts\":\"ops@greenstemglobal.com\",
        \"datadog_api_key\":\"YOUR_DATADOG_KEY\"
    }" \
    "Monitoring configuration for Continuum_Overworld $ENVIRONMENT"

echo "🎯 Secrets setup complete for $ENVIRONMENT environment!"

# Output GitHub secrets that need to be set
echo ""
echo "📋 GitHub Secrets to configure:"
echo "================================"
echo "COGNITO_USER_POOL_ID_${ENVIRONMENT^^}=$USER_POOL_ID"
echo "COGNITO_CLIENT_ID_${ENVIRONMENT^^}=$CLIENT_ID"
echo ""
echo "Manual GitHub secret setup:"
echo "gh secret set COGNITO_USER_POOL_ID_${ENVIRONMENT^^} -b '$USER_POOL_ID'"
echo "gh secret set COGNITO_CLIENT_ID_${ENVIRONMENT^^} -b '$CLIENT_ID'"
echo ""
echo "🔍 View all secrets:"
echo "aws secretsmanager list-secrets --region $REGION --query 'SecretList[?contains(Name, \`continuum/$ENVIRONMENT\`)].Name'"