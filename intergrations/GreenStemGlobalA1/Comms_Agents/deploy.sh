#!/bin/bash

# Comms Agents Deployment Script
# This script deploys the entire system to either local Docker or AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-local}
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME="comms-agents"

echo -e "${BLUE}🚀 Comms Agents Deployment Script${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Region: ${AWS_REGION}${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Local deployment
deploy_local() {
    print_info "Deploying to local environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_warning "No .env file found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    # Build and start services
    print_info "Building and starting Docker services..."
    docker-compose -f infra/docker-compose.yml down --remove-orphans
    docker-compose -f infra/docker-compose.yml build --no-cache
    docker-compose -f infra/docker-compose.yml up -d
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_info "Checking service health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Switchboard is healthy"
    else
        print_warning "Switchboard health check failed, but continuing..."
    fi
    
    if curl -f http://localhost:8001/api/v2/heartbeat > /dev/null 2>&1; then
        print_status "ChromaDB is healthy"
    else
        print_warning "ChromaDB health check failed, but continuing..."
    fi
    
    if curl -f http://localhost:15672/api/overview > /dev/null 2>&1; then
        print_status "RabbitMQ is healthy"
    else
        print_warning "RabbitMQ health check failed, but continuing..."
    fi
    
    print_status "Local deployment completed successfully!"
    print_info "Services available at:"
    print_info "  - Switchboard: http://localhost:8000"
    print_info "  - ChromaDB: http://localhost:8001"
    print_info "  - RabbitMQ Management: http://localhost:15672"
    print_info "  - Prometheus: http://localhost:9090"
    print_info "  - Grafana: http://localhost:3001 (admin/admin)"
}

# AWS deployment
deploy_aws() {
    print_info "Deploying to AWS environment..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Navigate to Terraform directory
    cd infra/aws/terraform
    
    # Initialize Terraform
    print_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_info "Planning deployment..."
    terraform plan -var-file="environments/${ENVIRONMENT}.tfvars" -out=tfplan
    
    # Confirm deployment
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled by user"
        exit 0
    fi
    
    # Apply deployment
    print_info "Applying deployment..."
    terraform apply tfplan
    
    # Get outputs
    print_info "Deployment completed! Getting service endpoints..."
    ALB_DNS=$(terraform output -raw alb_dns_name)
    ECR_URL=$(terraform output -raw ecr_repository_url)
    RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    CHROMADB_ENDPOINT=$(terraform output -raw chromadb_endpoint)
    
    print_status "AWS deployment completed successfully!"
    print_info "Services available at:"
    print_info "  - Switchboard: http://${ALB_DNS}"
    print_info "  - ECR Repository: ${ECR_URL}"
    print_info "  - RDS Endpoint: ${RDS_ENDPOINT}"
    print_info "  - Redis Endpoint: ${REDIS_ENDPOINT}"
    print_info "  - ChromaDB Endpoint: ${CHROMADB_ENDPOINT}"
    
    # Return to project root
    cd ../../..
}

# Deploy application to ECS
deploy_app_to_ecs() {
    print_info "Deploying application to ECS..."
    
    # Get ECR repository URL
    cd infra/aws/terraform
    ECR_URL=$(terraform output -raw ecr_repository_url)
    cd ../../..
    
    # Build and push Docker image
    print_info "Building Docker image..."
    docker build -f infra/Dockerfile -t ${PROJECT_NAME}:latest .
    
    print_info "Tagging image for ECR..."
    docker tag ${PROJECT_NAME}:latest ${ECR_URL}:latest
    
    print_info "Logging into ECR..."
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
    
    print_info "Pushing image to ECR..."
    docker push ${ECR_URL}:latest
    
    print_status "Application deployed to ECS successfully!"
}

# Run tests
run_tests() {
    print_info "Running tests..."
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip3 install -e .
    
    # Run tests
    print_info "Running test suite..."
    python3 -m pytest tests/ -v --tb=short
    
    print_status "Tests completed successfully!"
}

# Show logs
show_logs() {
    print_info "Showing service logs..."
    
    if [ "$ENVIRONMENT" = "local" ]; then
        docker-compose -f infra/docker-compose.yml logs -f
    else
        print_info "For AWS deployment, view logs in CloudWatch or run:"
        print_info "aws logs tail /ecs/comms-agents-switchboard --follow"
    fi
}

# Stop services
stop_services() {
    print_info "Stopping services..."
    
    if [ "$ENVIRONMENT" = "local" ]; then
        docker-compose -f infra/docker-compose.yml down
        print_status "Local services stopped"
    else
        print_info "For AWS deployment, services will continue running."
        print_info "To stop them, run: terraform destroy in the terraform directory"
    fi
}

# Main deployment logic
main() {
    case $ENVIRONMENT in
        "local")
            check_prerequisites
            deploy_local
            ;;
        "aws"|"production"|"staging")
            check_prerequisites
            deploy_aws
            deploy_app_to_ecs
            ;;
        "test")
            check_prerequisites
            run_tests
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_services
            ;;
        *)
            print_error "Invalid environment. Use: local, aws, production, staging, test, logs, or stop"
            echo "Usage: $0 [environment]"
            echo "  local      - Deploy to local Docker environment"
            echo "  aws        - Deploy to AWS"
            echo "  production - Deploy to AWS production environment"
            echo "  staging    - Deploy to AWS staging environment"
            echo "  test       - Run tests only"
            echo "  logs       - Show service logs"
            echo "  stop       - Stop local services"
            exit 1
            ;;
    esac
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Comms Agents Deployment Script"
        echo ""
        echo "Usage: $0 [environment]"
        echo ""
        echo "Environments:"
        echo "  local      - Deploy to local Docker environment"
        echo "  aws        - Deploy to AWS"
        echo "  production - Deploy to AWS production environment"
        echo "  staging    - Deploy to AWS staging environment"
        echo "  test       - Run tests only"
        echo "  logs       - Show service logs"
        echo "  stop       - Stop local services"
        echo ""
        echo "Examples:"
        echo "  $0 local           # Deploy locally"
        echo "  $0 aws             # Deploy to AWS"
        echo "  $0 test            # Run tests"
        echo "  $0 logs            # Show logs"
        echo "  $0 stop            # Stop services"
        exit 0
        ;;
esac

# Run main function
main "$@"

