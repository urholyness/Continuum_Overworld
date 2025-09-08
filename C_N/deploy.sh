#!/bin/bash
# C_N Foundation Deployment Script
# Execute Naivasha's v2.2.0 with precision tweaks

set -e
export AWS_PAGER=""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found"
    fi
    
    if ! command -v node &> /dev/null; then
        error "Node.js not found"
    fi
    
    if ! command -v zip &> /dev/null; then
        warn "zip not found, using tar for packaging"
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
    fi
    
    success "Prerequisites check passed"
}

# Set environment variables
set_environment() {
    log "Setting environment variables..."
    
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_REGION=$(aws configure get region || echo "us-east-1")
    
    # Generate secure tokens if not provided
    export C_N_API_TOKEN=${C_N_API_TOKEN:-$(openssl rand -hex 32)}
    export C_N_ORACLE_TOKEN=${C_N_ORACLE_TOKEN:-$(openssl rand -hex 32)}
    export C_N_HELIOS_TOKEN=${C_N_HELIOS_TOKEN:-$(openssl rand -hex 32)}
    
    # Blockchain configuration
    export ETH_RPC_URL=${ETH_RPC_URL:-"https://sepolia.infura.io/v3/YOUR_PROJECT_ID"}
    export LEDGER_CONTRACT_ADDRESS=${LEDGER_CONTRACT_ADDRESS:-"0x0000000000000000000000000000000000000000"}
    export LEDGER_EXPLORER_BASE="https://sepolia.etherscan.io"
    
    log "Environment configured for account: $AWS_ACCOUNT_ID in region: $AWS_REGION"
}

# Deploy CDK Foundation Stack
deploy_foundation() {
    log "Deploying CDK Foundation Stack..."
    
    cd infrastructure
    
    # Check if CDK is bootstrapped
    if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
        log "Bootstrapping CDK..."
        npx cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
    fi
    
    # Deploy stack
    npx cdk deploy CNFoundationStack --require-approval never || {
        warn "CDK deployment failed, continuing with manual setup..."
        return 1
    }
    
    cd ..
    success "Foundation stack deployed"
}

# Create IAM roles
create_iam_roles() {
    log "Creating IAM roles..."
    
    # Lambda execution role
    cat > lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role if it doesn't exist
    if ! aws iam get-role --role-name C_N-Lambda-Execution &> /dev/null; then
        aws iam create-role \
            --role-name C_N-Lambda-Execution \
            --assume-role-policy-document file://lambda-trust-policy.json \
            --description "C_N Lambda execution role"
        
        # Attach policies
        aws iam attach-role-policy \
            --role-name C_N-Lambda-Execution \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        aws iam attach-role-policy \
            --role-name C_N-Lambda-Execution \
            --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
        
        # Create inline policy for C_N permissions
        cat > c_n-permissions.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:/C_N/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:*:*:key/*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": ["secretsmanager.*.amazonaws.com", "cloudwatch.*.amazonaws.com"]
        }
      }
    }
  ]
}
EOF
        
        aws iam put-role-policy \
            --role-name C_N-Lambda-Execution \
            --policy-name C_N-Permissions \
            --policy-document file://c_n-permissions.json
        
        # Wait for role propagation
        sleep 10
    fi
    
    rm -f lambda-trust-policy.json c_n-permissions.json
    success "IAM roles configured"
}

# Package and deploy Lambda functions
deploy_lambdas() {
    log "Packaging and deploying Lambda functions..."
    
    # Ledger Signer
    log "Deploying Ledger Signer..."
    cd Ledger/Signer--Blockchain__PROD@v1.0.0
    
    if command -v zip &> /dev/null; then
        npm install --production
        zip -r function.zip . -x "*.git*" "*.DS_Store*" "node_modules/.cache/*"
    else
        npm install --production
        tar czf function.tar.gz --exclude='.git' --exclude='.DS_Store' --exclude='node_modules/.cache' .
        mv function.tar.gz function.zip
    fi
    
    # Deploy or update function
    if aws lambda get-function --function-name C_N-Ledger-Signer &> /dev/null; then
        aws lambda update-function-code \
            --function-name C_N-Ledger-Signer \
            --zip-file fileb://function.zip
    else
        aws lambda create-function \
            --function-name C_N-Ledger-Signer \
            --runtime nodejs18.x \
            --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/C_N-Lambda-Execution \
            --handler index.handler \
            --zip-file fileb://function.zip \
            --environment "Variables={CHAIN_RPC_URL_TESTNET=${ETH_RPC_URL},LEDGER_CONTRACT_TRACE=${LEDGER_CONTRACT_ADDRESS},LEDGER_EXPLORER_BASE=${LEDGER_EXPLORER_BASE}}" \
            --tracing-config Mode=Active \
            --timeout 30 \
            --description "C_N Ledger Signer - Blockchain transaction service"
    fi
    
    cd ../..
    success "Ledger Signer deployed"
    
    # MCP Gateway
    log "Deploying MCP Gateway..."
    cd MCP/Gateway--LLM__PROD@v0.1.0
    
    if command -v zip &> /dev/null; then
        npm install --production
        zip -r function.zip . -x "*.git*" "*.DS_Store*" "node_modules/.cache/*"
    else
        npm install --production
        tar czf function.tar.gz --exclude='.git' --exclude='.DS_Store' --exclude='node_modules/.cache' .
        mv function.tar.gz function.zip
    fi
    
    if aws lambda get-function --function-name C_N-MCP-Gateway &> /dev/null; then
        aws lambda update-function-code \
            --function-name C_N-MCP-Gateway \
            --zip-file fileb://function.zip
    else
        aws lambda create-function \
            --function-name C_N-MCP-Gateway \
            --runtime nodejs18.x \
            --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/C_N-Lambda-Execution \
            --handler index.handler \
            --zip-file fileb://function.zip \
            --tracing-config Mode=Active \
            --timeout 30 \
            --description "C_N MCP Gateway - LLM request routing with caching"
    fi
    
    cd ../..
    success "MCP Gateway deployed"
    
    # Token Authorizer
    log "Deploying Token Authorizer..."
    cd Aegis/Authorizer--Token__PROD@v1.0.0
    
    if command -v zip &> /dev/null; then
        npm install --production
        zip -r function.zip . -x "*.git*" "*.DS_Store*" "node_modules/.cache/*"
    else
        npm install --production
        tar czf function.tar.gz --exclude='.git' --exclude='.DS_Store' --exclude='node_modules/.cache' .
        mv function.tar.gz function.zip
    fi
    
    if aws lambda get-function --function-name C_N-Token-Authorizer &> /dev/null; then
        aws lambda update-function-code \
            --function-name C_N-Token-Authorizer \
            --zip-file fileb://function.zip
    else
        aws lambda create-function \
            --function-name C_N-Token-Authorizer \
            --runtime nodejs18.x \
            --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/C_N-Lambda-Execution \
            --handler index.handler \
            --zip-file fileb://function.zip \
            --environment "Variables={C_N_API_TOKEN=${C_N_API_TOKEN},C_N_ORACLE_TOKEN=${C_N_ORACLE_TOKEN},C_N_HELIOS_TOKEN=${C_N_HELIOS_TOKEN}}" \
            --timeout 10 \
            --description "C_N Token Authorizer - API Gateway custom authorizer"
    fi
    
    cd ../..
    success "Token Authorizer deployed"
}

# Create secrets in Secrets Manager
create_secrets() {
    log "Creating secrets..."
    
    if [ -z "$METAMASK_PRIVATE_KEY" ]; then
        warn "METAMASK_PRIVATE_KEY not provided, skipping secret creation"
        warn "Run: aws secretsmanager create-secret --name /C_N/PROD/Ledger/SignerKey --secret-string '{\"privateKey\":\"YOUR_KEY\"}'"
    else
        # Create or update ledger signer key
        if aws secretsmanager describe-secret --secret-id /C_N/PROD/Ledger/SignerKey &> /dev/null; then
            aws secretsmanager update-secret \
                --secret-id /C_N/PROD/Ledger/SignerKey \
                --secret-string "{\"privateKey\":\"${METAMASK_PRIVATE_KEY}\"}"
        else
            aws secretsmanager create-secret \
                --name /C_N/PROD/Ledger/SignerKey \
                --description "Ledger signer key (imported, not generated)" \
                --secret-string "{\"privateKey\":\"${METAMASK_PRIVATE_KEY}\"}"
        fi
        success "Ledger signer key stored in Secrets Manager"
    fi
    
    success "Secrets configured"
}

# Output deployment summary
output_summary() {
    log "Deployment Summary"
    echo "=================="
    
    echo -e "${GREEN}✅ C_N Foundation Deployed${NC}"
    echo ""
    echo -e "${BLUE}Lambda Functions:${NC}"
    echo "• C_N-Ledger-Signer"
    echo "• C_N-MCP-Gateway"
    echo "• C_N-Token-Authorizer"
    echo ""
    echo -e "${BLUE}API Tokens (save these):${NC}"
    echo "• C_N_API_TOKEN: $C_N_API_TOKEN"
    echo "• C_N_ORACLE_TOKEN: $C_N_ORACLE_TOKEN"
    echo "• C_N_HELIOS_TOKEN: $C_N_HELIOS_TOKEN"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Test health endpoints:"
    echo "   aws lambda invoke --function-name C_N-Ledger-Signer --payload '{\"httpMethod\":\"GET\",\"path\":\"/health\"}' response.json"
    echo "2. Deploy API Gateway (requires additional permissions)"
    echo "3. Connect to Amplify Console environment variables"
    echo "4. Deploy smart contracts to Sepolia testnet"
    echo ""
    echo -e "${YELLOW}⚠️  Manual steps required for full deployment due to permission constraints${NC}"
}

# Main execution
main() {
    log "Starting C_N Foundation Deployment v2.2.0"
    
    check_prerequisites
    set_environment
    create_iam_roles
    deploy_lambdas
    create_secrets
    
    # Try CDK deployment (may fail due to permissions)
    deploy_foundation || true
    
    output_summary
    
    success "C_N Foundation deployment completed!"
}

# Execute main function
main "$@"