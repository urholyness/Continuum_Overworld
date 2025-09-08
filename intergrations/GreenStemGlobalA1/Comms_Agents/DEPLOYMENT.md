# Comms Agents Deployment Guide

This guide covers deploying the Comms Agents system to both local and cloud environments.

## 🚀 Quick Start

### Local Deployment (Recommended for Development)
```bash
# Clone the repository
git clone <your-repo-url>
cd comms-agents

# Deploy locally
./deploy.sh local

# Or manually
docker-compose -f infra/docker-compose.yml up -d
```

### AWS Deployment (Production)
```bash
# Deploy to AWS
./deploy.sh aws

# Deploy to production
./deploy.sh production
```

## 📋 Prerequisites

### Local Development
- Docker & Docker Compose
- Python 3.11+
- Git

### AWS Deployment
- AWS CLI configured
- Terraform 1.0+
- Docker & Docker Compose
- Python 3.11+

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   ECS Cluster   │
│   (Optional)    │◄──►│   (ALB)         │◄──►│   (Fargate)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   RDS (PostgreSQL) │    │   ElastiCache   │
                       │   + pgvector      │    │   (Redis)       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ChromaDB      │    │   S3 Storage     │
                       │   (Vector DB)   │    │   (Knowledge)   │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Local Development Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start Services
```bash
# Start all services
docker-compose -f infra/docker-compose.yml up -d

# Check service status
docker-compose -f infra/docker-compose.yml ps

# View logs
docker-compose -f infra/docker-compose.yml logs -f
```

### 3. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Test endpoint
curl -X POST http://localhost:8000/draft/scribe \
  -H "Content-Type: application/json" \
  -d '{"issue_card_path":"issue_cards/eudr_smallholders.md","audience":"buyer","tone":"boardroom"}'
```

## ☁️ AWS Production Deployment

### 1. AWS Configuration
```bash
# Configure AWS CLI
aws configure

# Set default region
export AWS_DEFAULT_REGION=us-east-1

# Verify credentials
aws sts get-caller-identity
```

### 2. Terraform Setup
```bash
# Navigate to Terraform directory
cd infra/aws/terraform

# Initialize Terraform
terraform init

# Create environment configuration
cp environments/example.tfvars environments/production.tfvars

# Edit configuration
nano environments/production.tfvars
```

### 3. Deploy Infrastructure
```bash
# Plan deployment
terraform plan -var-file="environments/production.tfvars" -out=tfplan

# Apply deployment
terraform apply tfplan

# Get outputs
terraform output
```

### 4. Deploy Application
```bash
# Return to project root
cd ../../..

# Deploy application
./deploy.sh production
```

## 🔐 Security Configuration

### Environment Variables
```bash
# Required for production
JWT_SECRET=<strong-secret-key>
DATABASE_URL=<rds-connection-string>
REDIS_URL=<elasticache-connection-string>
OPENAI_API_KEY=<your-openai-key>
```

### Network Security
- VPC with private subnets for databases
- Security groups restricting access
- ALB in public subnets only
- ECS tasks in private subnets

### Data Encryption
- RDS encryption at rest
- S3 encryption at rest
- TLS for data in transit
- Secrets management via AWS Secrets Manager

## 📊 Monitoring & Observability

### CloudWatch Metrics
- ECS service metrics
- RDS performance insights
- ElastiCache metrics
- Custom application metrics

### Logging
- Centralized logging via CloudWatch
- Structured JSON logging
- Log retention policies
- Log analysis and alerting

### Health Checks
- ALB health checks
- ECS task health checks
- Application health endpoint
- Database connectivity checks

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python -m pytest
      - uses: aws-actions/configure-aws-credentials@v2
      - run: aws ecr get-login-password | docker login
      - run: docker build -t app .
      - run: docker push $ECR_REPOSITORY
      - run: terraform apply -auto-approve
```

## 🧪 Testing

### Run Tests
```bash
# Install dependencies
pip install -e .

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_scribe.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Scribe agent
curl -X POST http://localhost:8000/draft/scribe \
  -H "Content-Type: application/json" \
  -d '{"issue_card_path":"issue_cards/eudr_smallholders.md","audience":"buyer","tone":"boardroom"}'

# Signal agent
curl -X POST http://localhost:8000/scan/signal \
  -H "Content-Type: application/json" \
  -d '{"topics":["EUDR"],"focus_regions":["Kenya"]}'
```

## 📈 Scaling & Performance

### Auto-scaling Configuration
- CPU-based scaling (70% threshold)
- Memory-based scaling (80% threshold)
- Min/Max task count configuration
- Scale-in/out cooldown periods

### Performance Optimization
- Connection pooling for databases
- Redis caching layer
- CDN for static assets
- Load balancer optimization

### Cost Optimization
- Reserved instances for RDS
- Spot instances for non-critical workloads
- Auto-scaling to zero during off-peak
- Resource tagging for cost allocation

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check Docker logs
docker-compose -f infra/docker-compose.yml logs

# Check service status
docker-compose -f infra/docker-compose.yml ps

# Restart services
docker-compose -f infra/docker-compose.yml restart
```

#### Database Connection Issues
```bash
# Check database health
curl http://localhost:8000/health

# Verify environment variables
docker-compose -f infra/docker-compose.yml exec switchboard env | grep DATABASE

# Test database connection
docker-compose -f infra/docker-compose.yml exec postgres psql -U comms_user -d comms_db
```

#### AWS Deployment Issues
```bash
# Check Terraform state
terraform show

# Check AWS resources
aws ecs describe-services --cluster comms-agents-cluster

# View CloudWatch logs
aws logs tail /ecs/comms-agents-switchboard --follow
```

### Debug Commands
```bash
# Check all container statuses
docker ps -a

# View specific service logs
docker-compose -f infra/docker-compose.yml logs switchboard

# Execute commands in container
docker-compose -f infra/docker-compose.yml exec switchboard bash

# Check network connectivity
docker-compose -f infra/docker-compose.yml exec switchboard ping postgres
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

### Support
- GitHub Issues for bug reports
- Project Wiki for detailed guides
- Community forum for questions
- Professional support available

## 🔄 Maintenance

### Regular Tasks
- Security updates
- Dependency updates
- Backup verification
- Performance monitoring
- Cost optimization

### Backup Strategy
- Automated RDS snapshots
- S3 versioning enabled
- Cross-region replication
- Point-in-time recovery

### Update Process
1. Test in staging environment
2. Create backup snapshots
3. Deploy to production
4. Verify functionality
5. Monitor performance

---

**Need Help?** Check the troubleshooting section or open a GitHub issue for support.

