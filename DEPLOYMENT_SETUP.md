# 🚀 Continuum_Overworld Deployment Integration Setup

## Prerequisites Checklist
- ✅ AWS Account with login credentials
- ✅ MetaMask wallet configured
- ✅ GitHub account
- ⬜ AWS CLI installed locally
- ⬜ GitHub CLI installed locally
- ⬜ Node.js 20+ installed

---

## 🔧 Step 1: Initialize GitHub Repository

### Create Repository
```bash
# From Continuum_Overworld root
git init
git remote add origin https://github.com/YOUR_USERNAME/Continuum_Overworld.git

# Create .gitignore if not exists
cat > .gitignore << 'EOF'
# Environment
.env
.env.local
*.env

# Dependencies
node_modules/
.pnp
.pnp.js

# Production
build/
dist/
.next/
out/

# AWS
.aws/
amplify/
.amplify/

# Secrets
*.pem
*.key
*.cert
credentials.json

# Local data
postgres_data/
redpanda_data/
minio_data/
*.db

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log
npm-debug.log*
yarn-error.log*

# Testing
coverage/
.nyc_output/

# Blockchain
chain/artifacts/
chain/cache/
chain/typechain/
EOF

git add .
git commit -m "Initial commit: Continuum_Overworld foundation"
git branch -M main
git push -u origin main
```

---

## 🔐 Step 2: Set Up GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets to Add:
```yaml
# AWS Credentials
AWS_ACCESS_KEY_ID: YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY: YOUR_SECRET_KEY
AWS_REGION: us-east-1

# Database
PG_DSN: postgresql://bridge_admin:password@db-endpoint:5432/continuum

# Blockchain
ETH_RPC_URL: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
METAMASK_PRIVATE_KEY: YOUR_DEPLOYMENT_WALLET_PRIVATE_KEY
LEDGER_CONTRACT_ADDRESS: (will be set after deployment)

# API Keys
ACCUWEATHER_API_KEY: YOUR_KEY
SENTINELHUB_CLIENT_ID: YOUR_CLIENT_ID
SENTINELHUB_CLIENT_SECRET: YOUR_SECRET

# Cognito (will be created)
COGNITO_USER_POOL_ID: 
COGNITO_CLIENT_ID: 

# Amplify
AMPLIFY_APP_ID: (will be set after creation)
```

---

## 🌐 Step 3: AWS Configuration

### Install AWS CLI
```bash
# Windows (WSL2)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (us-east-1)
# Enter default output format (json)
```

### Create S3 Buckets for Deployment
```bash
# Create deployment bucket
aws s3 mb s3://continuum-overworld-deploy

# Create data lake bucket
aws s3 mb s3://continuum-overworld-lake

# Create website assets bucket
aws s3 mb s3://greenstem-global-assets
```

---

## 📦 Step 4: Set Up AWS Amplify

### Initialize Amplify for GreenStem Website
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0

# Install Amplify CLI globally
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init
# ? Enter a name for the project: greenstemglobal
# ? Enter a name for the environment: prod
# ? Choose your default editor: Visual Studio Code
# ? Choose the type of app: javascript
# ? What javascript framework: react
# ? Source Directory Path: src
# ? Distribution Directory Path: .next
# ? Build Command: npm run build
# ? Start Command: npm run start
# ? Do you want to use an AWS profile? Yes
# ? Please choose the profile you want to use: default

# Add hosting
amplify add hosting
# ? Select the plugin module to execute: Hosting with Amplify Console
# ? Choose a type: Manual deployment

# Push to create resources
amplify push
# ? Are you sure you want to continue? Yes

# Get the Amplify App ID
amplify status
# Note the App ID and add to GitHub Secrets as AMPLIFY_APP_ID
```

---

## 🔗 Step 5: Deploy Smart Contract

### Deploy to Sepolia
```bash
cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
ETH_RPC_URL=$ETH_RPC_URL
PRIVATE_KEY=$METAMASK_PRIVATE_KEY
EOF

# Compile and deploy
npx hardhat compile
npx hardhat run scripts/deploy.ts --network sepolia

# Save the deployed contract address
# Add to GitHub Secrets as LEDGER_CONTRACT_ADDRESS
```

---

## 🤖 Step 6: GitHub Actions Workflow

### Create Main Deployment Workflow
```bash
cat > .github/workflows/deploy-all.yml << 'EOF'
name: Deploy Continuum_Overworld

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  AWS_REGION: us-east-1
  NODE_VERSION: '20'

jobs:
  deploy-infrastructure:
    name: Deploy Core Infrastructure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy RDS PostgreSQL
        run: |
          cd infra/aws
          ./deploy-rds.sh ${{ github.event.inputs.environment || 'staging' }}
      
      - name: Deploy MSK Kafka
        run: |
          cd infra/aws
          ./deploy-msk.sh ${{ github.event.inputs.environment || 'staging' }}

  deploy-website:
    name: Deploy GreenStem Website
    runs-on: ubuntu-latest
    needs: deploy-infrastructure
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Install dependencies
        working-directory: ./Agora/Site--GreenStemGlobal__PROD@v1.0.0
        run: npm ci
      
      - name: Build application
        working-directory: ./Agora/Site--GreenStemGlobal__PROD@v1.0.0
        run: npm run build
        env:
          NEXT_PUBLIC_CHAIN_ID: 11155111
          ETH_RPC_URL: ${{ secrets.ETH_RPC_URL }}
          LEDGER_CONTRACT_ADDRESS: ${{ secrets.LEDGER_CONTRACT_ADDRESS }}
      
      - name: Deploy to Amplify
        run: |
          npm install -g @aws-amplify/cli
          cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
          amplify publish --yes

  deploy-apis:
    name: Deploy Lambda APIs
    runs-on: ubuntu-latest
    needs: deploy-infrastructure
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy Memory Bank API
        run: |
          cd The_Bridge/MemoryBank--API__DEV@v0.1.0
          zip -r function.zip .
          aws lambda update-function-code \
            --function-name memory-bank-api \
            --zip-file fileb://function.zip
      
      - name: Deploy CSR Ingestor
        run: |
          cd Forge/Ingestor--CSR__EU-DE@v1
          zip -r function.zip .
          aws lambda update-function-code \
            --function-name csr-ingestor \
            --zip-file fileb://function.zip

  verify-deployment:
    name: Verify Deployment
    runs-on: ubuntu-latest
    needs: [deploy-website, deploy-apis]
    steps:
      - uses: actions/checkout@v4
      
      - name: Run verification tests
        run: |
          cd infra
          python verify_deployment.py --env ${{ github.event.inputs.environment || 'staging' }}
      
      - name: Check website health
        run: |
          curl -f https://greenstemglobal.com/api/health || exit 1
      
      - name: Verify blockchain contract
        run: |
          cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain
          npx hardhat verify --network sepolia ${{ secrets.LEDGER_CONTRACT_ADDRESS }}
EOF

git add .github/workflows/deploy-all.yml
git commit -m "Add GitHub Actions deployment workflow"
git push
```

---

## 🛠️ Step 7: Local Development Integration

### Create Local Configuration
```bash
cat > .claude/config.json << 'EOF'
{
  "deployment": {
    "auto_deploy": true,
    "environments": {
      "local": {
        "command": "docker compose up -d",
        "health_check": "http://localhost:8088/health"
      },
      "staging": {
        "branch": "dev",
        "aws_account": "YOUR_ACCOUNT_ID",
        "region": "us-east-1"
      },
      "production": {
        "branch": "main",
        "aws_account": "YOUR_ACCOUNT_ID",
        "region": "us-east-1",
        "requires_approval": true
      }
    }
  },
  "services": {
    "database": {
      "local": "postgresql://bridge_admin:bridge_secure_2025@localhost:5432/continuum",
      "staging": "$PG_DSN_STAGING",
      "production": "$PG_DSN_PRODUCTION"
    },
    "blockchain": {
      "network": "sepolia",
      "contract": "$LEDGER_CONTRACT_ADDRESS",
      "rpc": "$ETH_RPC_URL"
    }
  },
  "triggers": {
    "on_commit": [
      "npm test",
      "npm run lint"
    ],
    "on_push": [
      "github_actions_deploy"
    ]
  }
}
EOF
```

### Create Deployment Helper Script
```bash
cat > deploy.sh << 'EOF'
#!/bin/bash

# Continuum_Overworld Deployment Script
set -e

ENVIRONMENT=${1:-staging}
COMPONENT=${2:-all}

echo "🚀 Deploying Continuum_Overworld to $ENVIRONMENT"

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat .env.$ENVIRONMENT | xargs)
fi

case $COMPONENT in
    "website")
        echo "📦 Deploying GreenStem Website..."
        cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
        npm run build
        amplify publish --yes
        ;;
    
    "contract")
        echo "⛓️ Deploying Smart Contract..."
        cd Agora/Site--GreenStemGlobal__PROD@v1.0.0/chain
        npx hardhat run scripts/deploy.ts --network sepolia
        ;;
    
    "infrastructure")
        echo "🏗️ Deploying Infrastructure..."
        cd infra
        cdk deploy --all --require-approval never
        ;;
    
    "all")
        $0 $ENVIRONMENT infrastructure
        $0 $ENVIRONMENT contract
        $0 $ENVIRONMENT website
        ;;
    
    *)
        echo "Usage: ./deploy.sh [environment] [component]"
        echo "Components: website, contract, infrastructure, all"
        exit 1
        ;;
esac

echo "✅ Deployment complete!"
EOF

chmod +x deploy.sh
```

---

## 🔄 Step 8: Set Up Auto-Deploy on Commit

### Create Git Hooks
```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

echo "🔍 Running pre-push checks..."

# Run tests
npm test

# Check for secrets
if git diff --cached --name-only | xargs grep -l "AWS_SECRET\|PRIVATE_KEY\|API_KEY"; then
    echo "❌ Error: Potential secrets detected in commit!"
    exit 1
fi

echo "✅ Pre-push checks passed!"
EOF

chmod +x .git/hooks/pre-push
```

### GitHub Branch Protection
```bash
# Set up branch protection via GitHub CLI
gh auth login
gh repo edit --default-branch main
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["continuous-integration"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

---

## 📊 Step 9: Monitoring Integration

### Create CloudWatch Dashboard
```bash
cat > infra/aws/cloudwatch-dashboard.json << 'EOF'
{
  "name": "Continuum-Overworld-Dashboard",
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          ["AWS/Lambda", "Errors", {"stat": "Sum"}],
          ["AWS/RDS", "DatabaseConnections"],
          ["AWS/S3", "BucketSizeBytes"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "System Health"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name Continuum-Overworld \
  --dashboard-body file://infra/aws/cloudwatch-dashboard.json
```

---

## 🎯 Step 10: Verify Integration

### Test Deployment Pipeline
```bash
# 1. Make a test change
echo "# Test deployment" >> README.md
git add README.md
git commit -m "test: Verify auto-deployment"
git push

# 2. Watch GitHub Actions
gh run watch

# 3. Verify deployment
curl https://greenstemglobal.com/api/health

# 4. Check blockchain
curl https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address=$LEDGER_CONTRACT_ADDRESS
```

---

## 📝 Environment Variables Summary

### Create .env files for each environment:

**.env.local**
```bash
NEXT_PUBLIC_SITE_ENV=local
NEXT_PUBLIC_BASE_URL=http://localhost:3000
PG_DSN=postgresql://bridge_admin:bridge_secure_2025@localhost:5432/continuum
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
MINIO_ENDPOINT=http://localhost:9000
```

**.env.staging**
```bash
NEXT_PUBLIC_SITE_ENV=staging
NEXT_PUBLIC_BASE_URL=https://staging.greenstemglobal.com
PG_DSN=$AWS_RDS_ENDPOINT_STAGING
KAFKA_BOOTSTRAP_SERVERS=$AWS_MSK_ENDPOINT_STAGING
```

**.env.production**
```bash
NEXT_PUBLIC_SITE_ENV=production
NEXT_PUBLIC_BASE_URL=https://greenstemglobal.com
PG_DSN=$AWS_RDS_ENDPOINT_PRODUCTION
KAFKA_BOOTSTRAP_SERVERS=$AWS_MSK_ENDPOINT_PRODUCTION
```

---

## ✅ Integration Complete!

You now have:
1. **GitHub as source of truth** with protected branches
2. **Automatic deployments** on push to main
3. **AWS resources** managed through IaC
4. **Blockchain contracts** deployed to Sepolia
5. **Local development** synced with cloud

### Next Commands to Run:
```bash
# 1. Initialize git and push
git init && git add . && git commit -m "Initial setup"
git remote add origin YOUR_GITHUB_URL
git push -u origin main

# 2. Deploy infrastructure
./deploy.sh staging infrastructure

# 3. Deploy contract
./deploy.sh staging contract

# 4. Deploy website
./deploy.sh staging website

# 5. Verify everything
cd infra && python verify_bridge.py
```

---

*Your system is now fully integrated! Any commit to main will trigger automatic deployment to AWS.*