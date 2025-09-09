#!/bin/bash
# C_N Enterprise Migration - Final Deployment
# Authority: George | PM: Naivasha
# Complete 3-day enterprise deployment

set -e
export AWS_PAGER=""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
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

enterprise() {
    echo -e "${PURPLE}🏢 $1${NC}"
}

# Pre-flight checks
check_prerequisites() {
    log "Checking enterprise deployment prerequisites..."
    
    # Check AWS CLI and credentials
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found"
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or expired"
    fi
    
    # Check CDK
    if ! command -v cdk &> /dev/null; then
        warn "CDK CLI not found globally, using npx"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js not found"
    fi
    
    # Verify we're in the right directory
    if [[ ! -f "cdk.json" ]]; then
        error "Not in CDK project root directory"
    fi
    
    success "Prerequisites validated"
}

# Set environment variables
setup_environment() {
    log "Setting up enterprise environment..."
    
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_REGION=$(aws configure get region || echo "us-east-1")
    
    # Generate secure tokens
    export C_N_API_TOKEN=${C_N_API_TOKEN:-$(openssl rand -hex 32)}
    export C_N_ORACLE_TOKEN=${C_N_ORACLE_TOKEN:-$(openssl rand -hex 32)}
    export C_N_HELIOS_TOKEN=${C_N_HELIOS_TOKEN:-$(openssl rand -hex 32)}
    export C_N_VIEWER_TOKEN=${C_N_VIEWER_TOKEN:-$(openssl rand -hex 32)}
    export C_N_PUBLIC_TOKEN=${C_N_PUBLIC_TOKEN:-$(openssl rand -hex 32)}
    
    # JWT secret for share links
    export JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 64)}
    
    # Blockchain configuration
    export ETH_RPC_URL=${ETH_RPC_URL:-"https://sepolia.infura.io/v3/YOUR_PROJECT_ID"}
    export LEDGER_CONTRACT_ADDRESS=${LEDGER_CONTRACT_ADDRESS:-"0x0000000000000000000000000000000000000000"}
    export SHARE_BASE_URL=${SHARE_BASE_URL:-"https://greenstemglobal.com"}
    
    enterprise "Environment configured for account: $AWS_ACCOUNT_ID"
    log "Region: $AWS_REGION"
    log "Share base URL: $SHARE_BASE_URL"
    
    success "Environment setup complete"
}

# Bootstrap CDK if needed
bootstrap_cdk() {
    log "Checking CDK bootstrap status..."
    
    if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
        log "Bootstrapping CDK for enterprise deployment..."
        npx cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION \
            --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
            --trust $AWS_ACCOUNT_ID \
            --trust-for-lookup $AWS_ACCOUNT_ID
        success "CDK bootstrap completed"
    else
        log "CDK already bootstrapped"
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing enterprise dependencies..."
    
    npm install --production=false
    
    success "Dependencies installed"
}

# Build TypeScript
build_project() {
    log "Building enterprise TypeScript project..."
    
    npm run build
    
    success "Project built successfully"
}

# Deploy stacks in dependency order
deploy_foundation() {
    enterprise "Deploying Foundation Stack (Core Infrastructure)..."
    
    npx cdk deploy CNFoundationStack \
        --require-approval never \
        --outputs-file foundation-outputs.json \
        --progress events
    
    success "Foundation stack deployed"
}

deploy_data() {
    enterprise "Deploying Data Stack (Read Models & DynamoDB)..."
    
    npx cdk deploy CNDataStack \
        --require-approval never \
        --outputs-file data-outputs.json \
        --progress events
    
    success "Data stack deployed"
}

deploy_services() {
    enterprise "Deploying Services Stack (Lambda Functions)..."
    
    # Set environment variables for Lambda functions
    export LAMBDA_ENV_VARS=$(cat << EOF
{
  "C_N_API_TOKEN": "$C_N_API_TOKEN",
  "C_N_ORACLE_TOKEN": "$C_N_ORACLE_TOKEN", 
  "C_N_HELIOS_TOKEN": "$C_N_HELIOS_TOKEN",
  "C_N_VIEWER_TOKEN": "$C_N_VIEWER_TOKEN",
  "C_N_PUBLIC_TOKEN": "$C_N_PUBLIC_TOKEN",
  "JWT_SECRET": "$JWT_SECRET",
  "ETH_RPC_URL": "$ETH_RPC_URL",
  "LEDGER_CONTRACT_ADDRESS": "$LEDGER_CONTRACT_ADDRESS",
  "SHARE_BASE_URL": "$SHARE_BASE_URL"
}
EOF
    )
    
    npx cdk deploy CNServicesStack \
        --require-approval never \
        --outputs-file services-outputs.json \
        --progress events
    
    success "Services stack deployed"
}

deploy_orchestration() {
    enterprise "Deploying Orchestration Stack (Step Functions)..."
    
    npx cdk deploy CNOrchestrationStack \
        --require-approval never \
        --outputs-file orchestration-outputs.json \
        --progress events
    
    success "Orchestration stack deployed"
}

deploy_api() {
    enterprise "Deploying API Stack (Public Boundary)..."
    
    npx cdk deploy CNApiStack \
        --require-approval never \
        --outputs-file api-outputs.json \
        --progress events
    
    success "Public API stack deployed"
}

deploy_observability() {
    enterprise "Deploying Observability Stack (Monitoring & Alerts)..."
    
    npx cdk deploy CNObservabilityStack \
        --require-approval never \
        --outputs-file observability-outputs.json \
        --progress events
    
    success "Observability stack deployed"
}

# Create secrets
create_secrets() {
    log "Creating enterprise secrets..."
    
    # Ledger signer key
    if [ ! -z "$METAMASK_PRIVATE_KEY" ]; then
        aws secretsmanager create-secret \
            --name /C_N/PROD/Ledger/SignerKey \
            --description "Ledger signer private key" \
            --secret-string "{\"privateKey\":\"$METAMASK_PRIVATE_KEY\"}" \
            --kms-key-id alias/Aegis_KMS__PROD 2>/dev/null || \
        aws secretsmanager update-secret \
            --secret-id /C_N/PROD/Ledger/SignerKey \
            --secret-string "{\"privateKey\":\"$METAMASK_PRIVATE_KEY\"}"
        
        success "Ledger signer key stored"
    else
        warn "METAMASK_PRIVATE_KEY not provided - manual secret creation required"
    fi
    
    # Sentinel Hub credentials
    if [ ! -z "$SENTINEL_CLIENT_ID" ] && [ ! -z "$SENTINEL_CLIENT_SECRET" ]; then
        aws secretsmanager create-secret \
            --name /C_N/PROD/Sentinel/Credentials \
            --description "Sentinel Hub API credentials" \
            --secret-string "{\"client_id\":\"$SENTINEL_CLIENT_ID\",\"client_secret\":\"$SENTINEL_CLIENT_SECRET\"}" \
            --kms-key-id alias/Aegis_KMS__PROD 2>/dev/null || \
        aws secretsmanager update-secret \
            --secret-id /C_N/PROD/Sentinel/Credentials \
            --secret-string "{\"client_id\":\"$SENTINEL_CLIENT_ID\",\"client_secret\":\"$SENTINEL_CLIENT_SECRET\"}"
        
        success "Sentinel Hub credentials stored"
    else
        warn "Sentinel Hub credentials not provided - manual secret creation required"
    fi
}

# Run smoke tests
run_smoke_tests() {
    log "Running enterprise smoke tests..."
    
    # Extract API URL from outputs
    API_URL=$(jq -r '.CNApiStack.ApiUrl // empty' api-outputs.json 2>/dev/null || echo "")
    
    if [ ! -z "$API_URL" ]; then
        # Test health endpoint
        log "Testing health endpoint..."
        HEALTH_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/health")
        
        if [ "$HEALTH_RESPONSE" = "200" ]; then
            success "Health endpoint responding"
        else
            warn "Health endpoint returned: $HEALTH_RESPONSE"
        fi
        
        # Test trace endpoint with auth
        log "Testing trace endpoint with authentication..."
        TRACE_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null \
            -H "Authorization: Bearer $C_N_VIEWER_TOKEN" \
            "$API_URL/public/trace/product?batchId=test")
        
        if [ "$TRACE_RESPONSE" = "404" ]; then
            success "Trace endpoint authenticated and responding (404 expected for test data)"
        else
            log "Trace endpoint returned: $TRACE_RESPONSE (may be expected)"
        fi
    else
        warn "API URL not found in outputs - skipping API tests"
    fi
    
    # Test Step Function if available
    SF_ARN=$(aws stepfunctions list-state-machines --query "stateMachines[?name=='Sat-Weather-Compose'].stateMachineArn" --output text 2>/dev/null || echo "")
    
    if [ ! -z "$SF_ARN" ] && [ "$SF_ARN" != "None" ]; then
        log "Testing Step Function execution..."
        
        EXECUTION_ARN=$(aws stepfunctions start-execution \
            --state-machine-arn "$SF_ARN" \
            --name "smoke-test-$(date +%s)" \
            --input '{"plotId":"smoke-test","correlationId":"'$(uuidgen)'","coordinates":{"lat":-0.3656,"lon":36.0822},"dateFrom":"2025-01-01"}' \
            --query 'executionArn' --output text 2>/dev/null || echo "")
        
        if [ ! -z "$EXECUTION_ARN" ]; then
            success "Step Function execution started: $(basename $EXECUTION_ARN)"
        else
            warn "Could not start Step Function execution - check permissions"
        fi
    else
        warn "Step Function not found - skipping workflow tests"
    fi
}

# Output deployment summary
output_summary() {
    enterprise "🎉 C_N Enterprise Migration Completed!"
    echo ""
    echo "==================== DEPLOYMENT SUMMARY ===================="
    echo ""
    echo -e "${GREEN}✅ Foundation Infrastructure${NC}"
    echo "  • KMS encryption with Aegis key"
    echo "  • EventBridge core bus with schema registry" 
    echo "  • Cost monitoring and anomaly detection"
    echo "  • SNS alerts configured"
    echo ""
    echo -e "${GREEN}✅ Data Layer${NC}"
    echo "  • ProductTrace read model (DynamoDB)"
    echo "  • FundsTrace read model (DynamoDB)" 
    echo "  • Satellite tiles index"
    echo "  • Point-in-time recovery enabled"
    echo ""
    echo -e "${GREEN}✅ Orchestration Layer${NC}"
    echo "  • Satellite-Weather-Compose workflow"
    echo "  • Ledger-Anchoring workflow"
    echo "  • Materialize-ReadModels workflow"
    echo "  • Error handling and DLQ configured"
    echo ""
    echo -e "${GREEN}✅ Public API Boundary${NC}"
    echo "  • Trace Composer (ONLY public data source)"
    echo "  • JWT-based share link generation"
    echo "  • API Gateway with WAF protection"
    echo "  • 5-minute response caching"
    echo ""
    echo -e "${GREEN}✅ Observability${NC}"
    echo "  • CloudWatch dashboards"
    echo "  • Critical alarms configured"
    echo "  • X-Ray tracing enabled"
    echo "  • Cost tracking and alerts"
    echo ""
    
    if [ -f api-outputs.json ]; then
        API_URL=$(jq -r '.CNApiStack.ApiUrl // "Not deployed"' api-outputs.json)
        echo -e "${BLUE}🔗 Public Endpoints:${NC}"
        echo "  • Health: $API_URL/health"
        echo "  • Product Trace: $API_URL/public/trace/product?batchId=24-0901-FB"
        echo "  • Funds Trace: $API_URL/public/trace/funds?contributionId=INV-2024-001"
        echo "  • Share Links: $API_URL/public/share"
        echo ""
    fi
    
    echo -e "${BLUE}🔑 API Tokens (SAVE THESE):${NC}"
    echo "  • C_N_API_TOKEN: $C_N_API_TOKEN"
    echo "  • C_N_ORACLE_TOKEN: $C_N_ORACLE_TOKEN"
    echo "  • C_N_HELIOS_TOKEN: $C_N_HELIOS_TOKEN"
    echo "  • C_N_VIEWER_TOKEN: $C_N_VIEWER_TOKEN"
    echo "  • C_N_PUBLIC_TOKEN: $C_N_PUBLIC_TOKEN"
    echo ""
    echo -e "${BLUE}📊 Monitoring:${NC}"
    echo "  • Dashboard: CloudWatch > Dashboards > C_N-Fleet-Health-Production"
    echo "  • Alarms: CloudWatch > Alarms (C_N-* prefix)"
    echo "  • X-Ray: X-Ray > Service Map"
    echo ""
    echo -e "${BLUE}💰 Cost Management:${NC}"
    echo "  • Daily budget: \$25 with 80% alerts"
    echo "  • Anomaly detection: Immediate alerts"
    echo "  • Estimated monthly: \$20-25"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "  1. Update Helios Console environment variables"
    echo "  2. Deploy smart contracts to Sepolia testnet"
    echo "  3. Configure Sentinel Hub API credentials"
    echo "  4. Test end-to-end workflows"
    echo "  5. Monitor dashboards for 24 hours"
    echo ""
    echo -e "${PURPLE}🏢 Enterprise Ready: Production-grade C_N architecture deployed${NC}"
    echo "============================================================="
}

# Main deployment orchestration
main() {
    enterprise "🚀 Starting C_N Enterprise Migration"
    echo ""
    
    check_prerequisites
    setup_environment
    bootstrap_cdk
    install_dependencies
    build_project
    
    # Deploy in dependency order
    deploy_foundation
    deploy_data
    deploy_services
    deploy_orchestration
    deploy_api
    deploy_observability
    
    create_secrets
    run_smoke_tests
    
    output_summary
    
    enterprise "🎯 C_N Enterprise Migration Complete!"
}

# Handle script arguments
case "$1" in
    "foundation")
        setup_environment && deploy_foundation
        ;;
    "data")
        setup_environment && deploy_data
        ;;
    "services")
        setup_environment && deploy_services
        ;;
    "api")
        setup_environment && deploy_api
        ;;
    "all"|"")
        main
        ;;
    *)
        echo "Usage: $0 [foundation|data|services|api|all]"
        echo "  foundation - Deploy core infrastructure only"
        echo "  data      - Deploy data layer only"
        echo "  services  - Deploy Lambda services only"
        echo "  api       - Deploy public API only"
        echo "  all       - Full enterprise deployment (default)"
        exit 1
        ;;
esac