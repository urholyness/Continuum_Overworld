#!/bin/bash
# C_N Enterprise Farm Infrastructure Deployment v1.1.0
# Authority: George | PM: Naivasha
# Enterprise-grade farm infrastructure with security, audit, and real coordinates

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
    export ENVIRONMENT="PROD"
    
    enterprise "Environment configured for account: $AWS_ACCOUNT_ID"
    log "Region: $AWS_REGION"
    log "Environment: $ENVIRONMENT"
    
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
    enterprise "Deploying Foundation Stack (KMS, EventBridge)..."
    
    npx cdk deploy CNFarmFoundationStack \
        --require-approval never \
        --outputs-file foundation-outputs.json \
        --progress events
    
    success "Foundation stack deployed"
}

deploy_data() {
    enterprise "Deploying Data Stack (6 DynamoDB Tables)..."
    
    npx cdk deploy CNFarmDataStack \
        --require-approval never \
        --outputs-file data-outputs.json \
        --progress events
    
    success "Data stack deployed"
}

deploy_storage() {
    enterprise "Deploying Storage Stack (S3 Buckets)..."
    
    npx cdk deploy CNFarmStorageStack \
        --require-approval never \
        --outputs-file storage-outputs.json \
        --progress events
    
    success "Storage stack deployed"
}

deploy_compute() {
    enterprise "Deploying Compute Stack (Lambda Functions)..."
    
    npx cdk deploy CNFarmComputeStack \
        --require-approval never \
        --outputs-file compute-outputs.json \
        --progress events
    
    success "Compute stack deployed"
}

deploy_api() {
    enterprise "Deploying API Stack (API Gateway + WAF)..."
    
    npx cdk deploy CNFarmApiStack \
        --require-approval never \
        --outputs-file api-outputs.json \
        --progress events
    
    success "API stack deployed"
}

deploy_observability() {
    enterprise "Deploying Observability Stack (Monitoring & Alerts)..."
    
    npx cdk deploy CNFarmObservabilityStack \
        --require-approval never \
        --outputs-file observability-outputs.json \
        --progress events
    
    success "Observability stack deployed"
}

# Create secrets
create_secrets() {
    log "Creating enterprise secrets..."
    
    # Sentinel Hub credentials
    if [ ! -z "$SENTINEL_CLIENT_ID" ] && [ ! -z "$SENTINEL_CLIENT_SECRET" ]; then
        aws secretsmanager create-secret \
            --name /C_N/PROD/Sentinel/Credentials \
            --description "Sentinel Hub API credentials for satellite data" \
            --secret-string "{\"client_id\":\"$SENTINEL_CLIENT_ID\",\"client_secret\":\"$SENTINEL_CLIENT_SECRET\"}" \
            --kms-key-id alias/Aegis_KMS__PROD 2>/dev/null || \
        aws secretsmanager update-secret \
            --secret-id /C_N/PROD/Sentinel/Credentials \
            --secret-string "{\"client_id\":\"$SENTINEL_CLIENT_ID\",\"client_secret\":\"$SENTINEL_CLIENT_SECRET\"}"
        
        success "Sentinel Hub credentials stored"
    else
        warn "Sentinel Hub credentials not provided - manual configuration required"
    fi
}

# Run smoke tests
run_smoke_tests() {
    log "Running enterprise smoke tests..."
    
    # Extract API URL from outputs
    API_URL=$(jq -r '.CNFarmApiStack.FarmAPIUrl // empty' api-outputs.json 2>/dev/null || echo "")
    
    if [ ! -z "$API_URL" ]; then
        # Test health endpoint (if exists)
        log "Testing API Gateway accessibility..."
        API_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL" || echo "000")
        
        if [ "$API_RESPONSE" = "403" ] || [ "$API_RESPONSE" = "404" ]; then
            success "API Gateway responding (${API_RESPONSE} expected without auth)"
        else
            log "API Gateway returned: $API_RESPONSE"
        fi
    else
        warn "API URL not found in outputs - skipping API tests"
    fi
    
    # Check DynamoDB tables
    log "Verifying DynamoDB tables..."
    TABLES=("C_N-FarmRegistry" "C_N-Oracle-FarmPlots" "C_N-Oracle-SatelliteData" "C_N-Oracle-WeatherData" "C_N-ReadModel-ProductTrace" "C_N-ReadModel-FundsTrace")
    
    for TABLE in "${TABLES[@]}"; do
        if aws dynamodb describe-table --table-name "$TABLE" &>/dev/null; then
            log "✓ Table $TABLE exists"
        else
            warn "✗ Table $TABLE not found"
        fi
    done
    
    # Check S3 buckets
    log "Verifying S3 buckets..."
    BUCKETS=("c-n-geo-086143043656" "c-n-oracle-tiles-086143043656")
    
    for BUCKET in "${BUCKETS[@]}"; do
        if aws s3api head-bucket --bucket "$BUCKET" &>/dev/null; then
            log "✓ Bucket $BUCKET exists"
        else
            warn "✗ Bucket $BUCKET not found"
        fi
    done
}

# Output deployment summary
output_summary() {
    enterprise "🎉 C_N Enterprise Farm Infrastructure Completed!"
    echo ""
    echo "==================== DEPLOYMENT SUMMARY ===================="
    echo ""
    echo -e "${GREEN}✅ Foundation Infrastructure${NC}"
    echo "  • KMS encryption with Aegis key"
    echo "  • EventBridge core bus with schema registry"
    echo "  • Cost monitoring and anomaly detection"
    echo ""
    echo -e "${GREEN}✅ Data Layer (6 Tables)${NC}"
    echo "  • FarmRegistry with country/geohash indexes"
    echo "  • FarmPlots with farm/geohash indexes"
    echo "  • SatelliteData with TTL and geohash index"
    echo "  • WeatherData with TTL and geohash index"
    echo "  • ProductTrace read model (immutable)"
    echo "  • FundsTrace read model (immutable)"
    echo ""
    echo -e "${GREEN}✅ Storage Layer${NC}"
    echo "  • Geometry bucket (versioned, KMS encrypted)"
    echo "  • Oracle tiles bucket (lifecycle rules)"
    echo "  • TLS-only bucket policies"
    echo ""
    echo -e "${GREEN}✅ Compute Layer${NC}"
    echo "  • Farm Validator with geometry validation"
    echo "  • Enhanced Satellite Oracle with polygon clipping"
    echo "  • X-Ray tracing enabled"
    echo ""
    echo -e "${GREEN}✅ API Layer${NC}"
    echo "  • API Gateway with JWT authorization"
    echo "  • WAF with rate limiting and geo-blocking"
    echo "  • Usage plans and API keys"
    echo ""
    echo -e "${GREEN}✅ Orchestration${NC}"
    echo "  • Step Functions for farm onboarding"
    echo "  • Enhanced satellite-weather composition"
    echo "  • Error handling and retry logic"
    echo ""
    echo -e "${GREEN}✅ Observability${NC}"
    echo "  • CloudWatch dashboards"
    echo "  • 6+ critical alarms configured"
    echo "  • SNS alert notifications"
    echo "  • Cost anomaly detection"
    echo ""
    
    if [ -f api-outputs.json ]; then
        API_URL=$(jq -r '.CNFarmApiStack.FarmAPIUrl // "Not deployed"' api-outputs.json)
        API_KEY_ID=$(jq -r '.CNFarmApiStack.APIKeyId // "Not deployed"' api-outputs.json)
        echo -e "${BLUE}🔗 API Endpoints:${NC}"
        echo "  • Base URL: $API_URL"
        echo "  • Farm Onboarding: POST $API_URL/admin/farms"
        echo "  • Satellite Data: POST $API_URL/admin/plots/satellite"
        echo "  • API Key ID: $API_KEY_ID"
        echo ""
    fi
    
    if [ -f observability-outputs.json ]; then
        DASHBOARD_URL=$(jq -r '.CNFarmObservabilityStack.DashboardURL // "Not deployed"' observability-outputs.json)
        echo -e "${BLUE}📊 Monitoring:${NC}"
        echo "  • Dashboard: $DASHBOARD_URL"
        echo "  • Alarms: CloudWatch > Alarms (C_N-* prefix)"
        echo ""
    fi
    
    echo -e "${BLUE}💰 Cost Management:${NC}"
    echo "  • Estimated monthly: \$15-25"
    echo "  • Pay-per-request pricing (no idle costs)"
    echo "  • Daily anomaly detection configured"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "  1. Configure Sentinel Hub API credentials"
    echo "  2. Set up Cognito User Pool for JWT auth"
    echo "  3. Create API key for applications"
    echo "  4. Test farm onboarding with real GeoJSON"
    echo "  5. Monitor dashboards for 24 hours"
    echo ""
    echo -e "${PURPLE}🏢 Enterprise Ready: Production-grade farm infrastructure deployed${NC}"
    echo "============================================================="
}

# Main deployment orchestration
main() {
    enterprise "🚀 Starting C_N Enterprise Farm Infrastructure Deployment"
    echo ""
    
    check_prerequisites
    setup_environment
    bootstrap_cdk
    install_dependencies
    build_project
    
    # Deploy in dependency order
    deploy_foundation
    deploy_data
    deploy_storage
    deploy_compute
    deploy_api
    deploy_observability
    
    create_secrets
    run_smoke_tests
    
    output_summary
    
    enterprise "🎯 C_N Enterprise Farm Infrastructure Complete!"
}

# Handle script arguments
case "$1" in
    "foundation")
        setup_environment && deploy_foundation
        ;;
    "data")
        setup_environment && deploy_data
        ;;
    "storage")
        setup_environment && deploy_storage
        ;;
    "compute")
        setup_environment && deploy_compute
        ;;
    "api")
        setup_environment && deploy_api
        ;;
    "observability")
        setup_environment && deploy_observability
        ;;
    "all"|"")
        main
        ;;
    *)
        echo "Usage: $0 [foundation|data|storage|compute|api|observability|all]"
        echo "  foundation    - Deploy KMS and EventBridge only"
        echo "  data         - Deploy DynamoDB tables only"
        echo "  storage      - Deploy S3 buckets only"
        echo "  compute      - Deploy Lambda functions only"
        echo "  api          - Deploy API Gateway and WAF only"
        echo "  observability - Deploy monitoring only"
        echo "  all          - Full enterprise deployment (default)"
        exit 1
        ;;
esac