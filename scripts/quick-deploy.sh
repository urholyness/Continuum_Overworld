#!/bin/bash

# Quick deployment script for Continuum_Overworld
# Usage: ./scripts/quick-deploy.sh [environment] [component]

set -e

ENVIRONMENT=${1:-staging}
COMPONENT=${2:-all}
REGION=${AWS_REGION:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Continuum_Overworld Quick Deploy${NC}"
echo -e "${BLUE}Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "${BLUE}Component: ${YELLOW}$COMPONENT${NC}"
echo -e "${BLUE}Region: ${YELLOW}$REGION${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found. Please install Node.js 20+.${NC}"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git not found. Please install Git.${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure'.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${BLUE}🏗️ Deploying infrastructure for $ENVIRONMENT...${NC}"
    
    # Setup secrets
    if [ -f "scripts/setup-secrets.sh" ]; then
        chmod +x scripts/setup-secrets.sh
        ./scripts/setup-secrets.sh $ENVIRONMENT
    fi
    
    # Deploy RDS
    if [ -f "infra/aws/deploy-rds.sh" ]; then
        chmod +x infra/aws/deploy-rds.sh
        ./infra/aws/deploy-rds.sh $ENVIRONMENT
    fi
    
    # Deploy MSK
    if [ -f "infra/aws/deploy-msk.sh" ]; then
        chmod +x infra/aws/deploy-msk.sh
        ./infra/aws/deploy-msk.sh $ENVIRONMENT
    fi
    
    echo -e "${GREEN}✅ Infrastructure deployed${NC}"
}

# Deploy smart contracts
deploy_blockchain() {
    echo -e "${BLUE}⛓️ Deploying smart contracts...${NC}"
    
    if [ -f "scripts/deploy-blockchain.sh" ]; then
        chmod +x scripts/deploy-blockchain.sh
        ./scripts/deploy-blockchain.sh $ENVIRONMENT sepolia
    else
        echo -e "${YELLOW}⚠️ Blockchain deployment script not found${NC}"
    fi
    
    echo -e "${GREEN}✅ Smart contracts deployed${NC}"
}

# Deploy website
deploy_website() {
    echo -e "${BLUE}🌐 Deploying GreenStem Global website...${NC}"
    
    cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing dependencies...${NC}"
        npm install
    fi
    
    # Build application
    echo -e "${YELLOW}🔨 Building application...${NC}"
    npm run build
    
    # Deploy with Amplify CLI
    if ! command -v amplify &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Amplify CLI...${NC}"
        npm install -g @aws-amplify/cli
    fi
    
    # Initialize if not already done
    if [ ! -f "amplify/.config/project-config.json" ]; then
        echo -e "${YELLOW}⚙️ Initializing Amplify project...${NC}"
        amplify init --yes
        amplify add hosting --yes
    fi
    
    # Deploy
    amplify publish --yes
    
    cd - > /dev/null
    echo -e "${GREEN}✅ Website deployed${NC}"
}

# Deploy APIs
deploy_apis() {
    echo -e "${BLUE}🔌 Deploying Lambda APIs...${NC}"
    
    # Memory Bank API
    if [ -d "The_Bridge/MemoryBank--API__DEV@v0.1.0" ]; then
        cd The_Bridge/MemoryBank--API__DEV@v0.1.0
        
        # Create deployment package
        zip -r memory-bank-api.zip . -x "*.git*" "*.pyc" "__pycache__/*" "*.pytest_cache*"
        
        # Deploy to Lambda
        aws lambda create-function \
            --function-name "continuum-memory-bank-api-$ENVIRONMENT" \
            --runtime python3.11 \
            --role "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role" \
            --handler app.handler \
            --zip-file fileb://memory-bank-api.zip \
            --timeout 30 \
            --memory-size 512 \
            --region $REGION || \
        aws lambda update-function-code \
            --function-name "continuum-memory-bank-api-$ENVIRONMENT" \
            --zip-file fileb://memory-bank-api.zip \
            --region $REGION
        
        rm -f memory-bank-api.zip
        cd - > /dev/null
    fi
    
    echo -e "${GREEN}✅ APIs deployed${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${BLUE}🧪 Verifying deployment...${NC}"
    
    # Wait for services to start
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 30
    
    # Test website
    if [ "$ENVIRONMENT" = "production" ]; then
        URL="https://greenstemglobal.com"
    else
        URL="https://staging.greenstemglobal.com"
    fi
    
    echo -e "${YELLOW}🌐 Testing website: $URL${NC}"
    if curl -f "$URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Website is responding${NC}"
    else
        echo -e "${YELLOW}⚠️ Website not yet available (may need more time)${NC}"
    fi
    
    # Test API endpoints
    if curl -f "$URL/api/trace/lots" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API endpoints responding${NC}"
    else
        echo -e "${YELLOW}⚠️ API endpoints not yet available${NC}"
    fi
    
    echo -e "${GREEN}✅ Verification complete${NC}"
}

# Main deployment logic
main() {
    check_prerequisites
    
    case $COMPONENT in
        "infrastructure" | "infra")
            deploy_infrastructure
            ;;
        
        "blockchain" | "contract")
            deploy_blockchain
            ;;
        
        "website" | "web")
            deploy_website
            ;;
        
        "apis" | "lambda")
            deploy_apis
            ;;
        
        "verify" | "test")
            verify_deployment
            ;;
        
        "all")
            deploy_infrastructure
            deploy_blockchain
            deploy_website
            deploy_apis
            verify_deployment
            ;;
        
        *)
            echo -e "${RED}❌ Unknown component: $COMPONENT${NC}"
            echo -e "${BLUE}Available components:${NC}"
            echo -e "  ${YELLOW}infrastructure${NC} - Deploy RDS, MSK, secrets"
            echo -e "  ${YELLOW}blockchain${NC}     - Deploy smart contracts"
            echo -e "  ${YELLOW}website${NC}        - Deploy Next.js website"
            echo -e "  ${YELLOW}apis${NC}           - Deploy Lambda functions"
            echo -e "  ${YELLOW}verify${NC}         - Test deployment"
            echo -e "  ${YELLOW}all${NC}            - Deploy everything"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}🎉 Deployment complete!${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "${GREEN}🌐 Website: https://greenstemglobal.com${NC}"
    else
        echo -e "${GREEN}🌐 Website: https://staging.greenstemglobal.com${NC}"
    fi
    
    # Get contract address from secrets
    if aws secretsmanager describe-secret --secret-id "continuum/$ENVIRONMENT/blockchain" --region $REGION > /dev/null 2>&1; then
        CONTRACT_ADDRESS=$(aws secretsmanager get-secret-value --secret-id "continuum/$ENVIRONMENT/blockchain" --query SecretString --output text --region $REGION | jq -r '.contract_address')
        if [ "$CONTRACT_ADDRESS" != "null" ] && [ "$CONTRACT_ADDRESS" != "WILL_BE_SET_AFTER_DEPLOYMENT" ]; then
            echo -e "${GREEN}⛓️ Contract: https://sepolia.etherscan.io/address/$CONTRACT_ADDRESS${NC}"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "1. ${YELLOW}Test all functionality${NC}"
    echo -e "2. ${YELLOW}Update DNS records (if needed)${NC}"
    echo -e "3. ${YELLOW}Configure monitoring alerts${NC}"
    echo -e "4. ${YELLOW}Run load tests${NC}"
}

# Handle script interruption
trap 'echo -e "\n${RED}❌ Deployment interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"