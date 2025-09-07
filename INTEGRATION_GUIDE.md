# 🤝 Claude Code Integration Guide

## Setting Up Your Development Environment

### Prerequisites ✅
- AWS Account with credentials
- MetaMask wallet configured
- GitHub repository access
- Node.js 20+ installed

---

## 🚀 Quick Start (5 Minutes)

### 1. Initial Setup
```bash
# Clone and setup
cd /mnt/c/users/password/Continuum_Overworld
git init
git remote add origin https://github.com/YOUR_USERNAME/Continuum_Overworld.git

# Make scripts executable
chmod +x scripts/*.sh
chmod +x infra/aws/*.sh

# Install global dependencies
npm install -g @aws-amplify/cli
```

### 2. Configure AWS
```bash
# Configure AWS CLI
aws configure
# Enter your Access Key, Secret Key, Region (us-east-1), Output (json)

# Test connection
aws sts get-caller-identity
```

### 3. Set Environment Variables
```bash
# Create .env file
cat > .env.local << 'EOF'
# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=YOUR_ACCOUNT_ID

# MetaMask
METAMASK_PRIVATE_KEY=0xYOUR_PRIVATE_KEY

# External APIs (get these from providers)
ACCUWEATHER_API_KEY=your_key
SENTINELHUB_CLIENT_ID=your_id
SENTINELHUB_CLIENT_SECRET=your_secret
EOF

# Load variables
source .env.local
```

### 4. Quick Deploy
```bash
# Deploy everything to staging
./scripts/quick-deploy.sh staging all

# Or deploy components individually:
./scripts/quick-deploy.sh staging infrastructure
./scripts/quick-deploy.sh staging blockchain
./scripts/quick-deploy.sh staging website
```

---

## 🔄 Claude Code Integration Commands

### When Working with Claude Code, Use These Commands:

#### **Deploy on Every Commit** 
```bash
# Setup auto-deploy (run once)
git add .
git commit -m "Setup Continuum_Overworld integration"
git push origin main  # This triggers GitHub Actions
```

#### **Manual Deploy from Claude**
```bash
# Deploy specific environment
./scripts/quick-deploy.sh staging website

# Deploy all components
./scripts/quick-deploy.sh production all

# Just test deployment
./scripts/quick-deploy.sh staging verify
```

#### **Local Development**
```bash
# Start local environment
cd infra
docker compose up -d

# Verify everything is running
python verify_bridge.py

# Check services
docker ps
curl http://localhost:8088/health  # Memory Bank API
curl http://localhost:3000         # Website (if running locally)
```

---

## 🔐 GitHub Secrets Configuration

### Required Secrets (Set These in GitHub):
```bash
# Go to: GitHub Repo → Settings → Secrets → Actions
# Add these secrets:

AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
METAMASK_PRIVATE_KEY=0x...

# API Keys
ACCUWEATHER_API_KEY=...
SENTINELHUB_CLIENT_ID=...
SENTINELHUB_CLIENT_SECRET=...
```

### Auto-Setup Secrets Script:
```bash
# This script creates AWS secrets and sets GitHub secrets
./scripts/setup-secrets.sh staging
./scripts/setup-secrets.sh production
```

---

## 📊 Monitoring & Status Checks

### Health Checks
```bash
# Check website status
curl https://staging.greenstemglobal.com/api/health
curl https://greenstemglobal.com/api/health

# Check blockchain contract
curl "https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address=$CONTRACT_ADDRESS"

# Check AWS services
aws rds describe-db-instances --db-instance-identifier continuum-staging
aws kafka list-clusters --region us-east-1
```

### View Logs
```bash
# GitHub Actions logs
gh run list
gh run view --log

# AWS CloudWatch logs
aws logs tail /aws/lambda/continuum-memory-bank-api-staging --follow

# Local logs
docker compose logs -f
```

---

## 🧪 Testing Integration

### Test Sequence
```bash
# 1. Test local environment
cd infra && python verify_bridge.py

# 2. Deploy to staging
./scripts/quick-deploy.sh staging all

# 3. Run integration tests
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
npm test

# 4. Test website endpoints
curl https://staging.greenstemglobal.com/api/trace/lots
curl https://staging.greenstemglobal.com/api/trace/funds

# 5. Test blockchain interaction
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain
npx hardhat test
```

### Automated Tests
```bash
# Unit tests
npm test

# Integration tests
python infra/test_pipeline_e2e.py

# Security scan
npm audit
git secrets --scan
```

---

## 🔀 Git Workflow Integration

### Branch Strategy
```bash
# Development workflow
git checkout -b feature/your-feature
# Make changes...
git commit -m "feat: add new feature"
git push origin feature/your-feature
# Create PR → merges to dev → triggers staging deploy

# Production workflow
git checkout main
git merge dev
git push origin main  # Triggers production deploy (with approval)
```

### Commit Hooks
```bash
# Pre-commit checks (automatically installed)
# - Runs tests
# - Checks for secrets
# - Validates code format

# Pre-push checks
# - Security scan
# - Dependency audit
# - Build verification
```

---

## 📱 Claude Code Specific Commands

### When Claude Code Asks "Should I Deploy This?"
```bash
# For staging changes
./scripts/quick-deploy.sh staging website

# For production (requires approval)
./scripts/quick-deploy.sh production all
```

### Environment-Specific Operations
```bash
# Check current environment
aws sts get-caller-identity
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `continuum`)].Name'

# Switch between environments
export ENVIRONMENT=staging    # or production
export AWS_REGION=us-east-1

# Get environment info
aws secretsmanager get-secret-value --secret-id "continuum/$ENVIRONMENT/database"
```

### Emergency Rollback
```bash
# Rollback website
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
git revert HEAD
git push origin main

# Rollback infrastructure (if needed)
aws rds describe-db-snapshots --db-instance-identifier continuum-production
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier continuum-production-rollback --db-snapshot-identifier rds:continuum-production-YYYY-MM-DD-HH-mm
```

---

## 🎯 Claude Code Common Tasks

### 1. "Add a New Feature to GreenStem Website"
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
# Make code changes
npm run build
./scripts/quick-deploy.sh staging website
# Test on staging
./scripts/quick-deploy.sh production website  # After approval
```

### 2. "Update Smart Contract"
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain
# Modify contract
npx hardhat compile
npx hardhat test
./scripts/deploy-blockchain.sh staging sepolia
# Update frontend with new contract address
```

### 3. "Scale Infrastructure"
```bash
# Update RDS instance class
aws rds modify-db-instance --db-instance-identifier continuum-production --db-instance-class db.t3.large --apply-immediately

# Add more Kafka brokers
aws kafka update-broker-count --cluster-arn $CLUSTER_ARN --current-version $CURRENT_VERSION --target-number-of-broker-nodes 4
```

### 4. "Add New API Endpoint"
```bash
# Add route to Next.js
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/src/app/api
# Create new route.ts file
npm run build
./scripts/quick-deploy.sh staging website
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Amplify Deployment Failed"
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
amplify status
amplify diagnose
# Fix issues and retry
amplify push
```

#### 2. "RDS Connection Refused"
```bash
# Check security group
aws ec2 describe-security-groups --group-names continuum-rds-sg-staging

# Check if RDS is running
aws rds describe-db-instances --db-instance-identifier continuum-staging

# Test connection
psql $PG_DSN -c "SELECT version();"
```

#### 3. "Smart Contract Deployment Failed"
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain
npx hardhat compile --force
# Check private key is set
echo $METAMASK_PRIVATE_KEY | cut -c1-10
# Check ETH balance
npx hardhat run scripts/check-balance.js --network sepolia
```

#### 4. "GitHub Actions Failing"
```bash
# Check secrets
gh secret list

# View logs
gh run list
gh run view --log

# Re-run failed jobs
gh run rerun --failed-only
```

---

## 📞 Support Commands

### Get System Status
```bash
./scripts/system-status.sh  # Custom script to check everything
aws cloudwatch get-dashboard --dashboard-name Continuum-Overworld
```

### Emergency Contacts
```bash
# If something goes wrong:
echo "Technical: dev@greenstemglobal.com"
echo "Business: info@greenstemglobal.com" 
echo "AWS Support: Create case in AWS Console"
```

---

## 🎉 Success Checklist

After integration, verify:
- [ ] Local development environment works (`docker compose up -d`)
- [ ] GitHub Actions deploy successfully (`gh run list`)
- [ ] Staging website loads (`https://staging.greenstemglobal.com`)
- [ ] API endpoints return data (`/api/trace/lots`, `/api/trace/funds`)
- [ ] Smart contract is deployed and verified on Etherscan
- [ ] Production deployment works (with approval)
- [ ] Monitoring alerts are configured

---

*You're now integrated with Continuum_Overworld! 🚀*

**Key Command**: `./scripts/quick-deploy.sh [env] [component]`

This is your main deployment tool that Claude Code will use.