# Continuum Overworld Deployment Blueprint v2.0

## 🚀 Deployment Status: SUCCESS ✅
**Last Updated**: September 2025  
**Environment**: Production (Amplify)  
**Build Status**: Functional and Stable  

---

## Executive Summary

The Continuum Overworld monorepo has been successfully deployed using AWS Amplify with a specialized configuration that handles the complex monorepo structure. This blueprint documents the proven deployment strategy and provides templates for future applications.

### Key Success Metrics
- ✅ **Deployment Success Rate**: 100% after architecture fixes
- ✅ **Build Time**: Optimized with proper caching
- ✅ **Cost Efficiency**: ~$20-25/month operational cost
- ✅ **Enterprise Integration**: Full C_N platform connectivity

---

## Architecture Overview

### Monorepo Structure
```
Continuum_Overworld/                    # Repository Root
├── amplify.yml                         # ⚠️ ROOT AMPLIFY CONFIG (Critical)
├── package.json                        # Minimal metadata only
├── CONTRIBUTING.md                     # AWS Amplify commit guidelines
├── 
├── Agora/                              # 🌐 Web Applications Division
│   └── Site--GreenStemGlobal__PROD@v1.0.0/   # Main Production App
│       ├── amplify.yml                 # App-specific config
│       ├── package.json               # Next.js dependencies
│       ├── .env.example               # App environment variables
│       └── src/                       # Application source
│
├── C_N/                               # 🏢 Enterprise Platform (Continuum_Nexus)
│   ├── infrastructure/               # CDK infrastructure stacks
│   └── lib/                         # Enterprise business logic
│
├── Ledger/                           # ⛓️ Blockchain Contracts
├── The_Bridge/                       # 🎛️ Control Surface
├── infra/                           # 🏗️ Infrastructure as Code
└── validation/                      # ✅ Testing & Validation
```

---

## 🔧 Critical Deployment Configuration

### 1. Root Level Amplify Configuration
**File**: `/amplify.yml` (Repository Root)

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "Starting build in Agora/Site--GreenStemGlobal__PROD@v1.0.0"
        - cd Agora/Site--GreenStemGlobal__PROD@v1.0.0
        - echo "Current directory after cd:"
        - pwd
        - echo "Installing dependencies..."
        - npm ci
    build:
      commands:
        - echo "Building Next.js application"
        - echo "Current directory in build phase:"
        - pwd
        - npm run build
        - echo "Build completed successfully"
  artifacts:
    baseDirectory: Agora/Site--GreenStemGlobal__PROD@v1.0.0/.next
    files:
      - '**/*'
  cache:
    paths:
      - Agora/Site--GreenStemGlobal__PROD@v1.0.0/node_modules/**/*
```

**🚨 CRITICAL NOTES:**
- **Single CD Command**: Only change directory in `preBuild` phase
- **Directory Context**: Build phase inherits directory from preBuild
- **Artifact Path**: Must point to subdirectory's `.next` folder
- **Cache Strategy**: Cache at app level, not root level

### 2. Application Package Configuration
**File**: `/Agora/Site--GreenStemGlobal__PROD@v1.0.0/package.json`

```json
{
  "name": "gsg-web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "ethers": "^6.13.2",
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "zod": "^3.23.8"
  }
}
```

### 3. Environment Variable Strategy

#### App-Level Variables (`.env.example`)
```bash
# Next.js Application Configuration
NEXT_PUBLIC_SITE_ENV=staging
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_CHAIN_ID=11155111

# Blockchain Integration
ETH_RPC_URL=
LEDGER_CONTRACT_ADDRESS=

# AWS Cognito Authentication
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
```

#### Root-Level Variables (Enterprise Data)
```bash
# Enterprise Data Extraction APIs
LUFTHANSA_API_KEY=
AFKLM_API_KEY=
MAERSK_API_KEY=
OPENWEATHER_API_KEY=

# LLM Integration
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

---

## 🔄 Deployment Process (Step-by-Step)

### For New Applications in Monorepo:

1. **Create Application Directory**
   ```bash
   mkdir -p Agora/App--YourAppName__PROD@v1.0.0
   cd Agora/App--YourAppName__PROD@v1.0.0
   ```

2. **Initialize Next.js Application**
   ```bash
   npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir
   ```

3. **Update Root Amplify Configuration**
   ```yaml
   # Update paths in /amplify.yml
   - cd Agora/App--YourAppName__PROD@v1.0.0
   # Update baseDirectory and cache paths accordingly
   ```

4. **Configure Environment Variables**
   - Copy `.env.example` template
   - Configure in Amplify Console: App Settings → Environment Variables

5. **Test Local Build**
   ```bash
   npm install
   npm run build
   ```

6. **Deploy with Safe Commit Message**
   ```bash
   git add .
   git commit -m "Add new production app deployment configuration"
   git push origin main
   ```

---

## 🏢 Enterprise Architecture Integration

### C_N Platform Connectivity
The deployment integrates with the enterprise **Continuum_Nexus (C_N)** platform:

- **Step Functions**: Orchestrate farm data processing workflows
- **DynamoDB**: Store processed agricultural data with enterprise security
- **API Gateway**: JWT-authenticated APIs for data access
- **EventBridge**: Real-time event processing for satellite data
- **Lambda Functions**: Serverless processing of geospatial data
- **S3 Buckets**: Secure storage with KMS encryption

### Blockchain Integration (Ledger)
- **Network**: Sepolia Testnet (Chain ID: 11155111)
- **Contracts**: Deployed via Hardhat framework
- **Integration**: Ethers.js v6 for web3 connectivity
- **Traceability**: Immutable anchoring of agricultural data

---

## 📋 Commit Message Guidelines (AWS Amplify Compatible)

### ✅ SAFE Characters:
- Letters and numbers
- Spaces, dashes (-), underscores (_)
- Periods (.), commas (,)

### ❌ AVOID These Characters:
- `:` (colon) - Breaks YAML parsing
- `|` (pipe) - Breaks YAML parsing  
- `>` (greater-than) - Breaks YAML parsing
- `&` (ampersand) - Breaks YAML parsing
- `*` (asterisk) - Breaks YAML parsing
- `@` (excessive at symbols)

### Examples:
```bash
# ✅ Good
git commit -m "Add farm validation Lambda with geospatial indexing"
git commit -m "Update DynamoDB tables for KMS encryption"
git commit -m "Fix build configuration for Amplify deployment"

# ❌ Bad  
git commit -m "feat: Add new feature"          # Colon breaks YAML
git commit -m "Update config | Deploy to prod" # Pipe breaks YAML
```

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: "sh: 1: cd: can't cd to [directory]"
**Cause**: Duplicate `cd` commands in build phases
**Solution**: Ensure only ONE `cd` command in `preBuild` phase

### Issue 2: Build artifacts not found
**Cause**: Incorrect `baseDirectory` path
**Solution**: Point to `AppDirectory/.next` not root `.next`

### Issue 3: Dependencies not found during build
**Cause**: Cache paths pointing to wrong directory
**Solution**: Cache `AppDirectory/node_modules/**/*`

### Issue 4: Commit triggers deployment failure
**Cause**: Special characters in commit message
**Solution**: Use simple, descriptive commit messages without colons or pipes

---

## 🔐 Security & Access Configuration

### AWS Amplify Team Provider
```json
{
  "dev": {
    "awscloudformation": {
      "AuthRoleName": "amplify-gsg-web-dev-authRole",
      "UnauthRoleName": "amplify-gsg-web-dev-unauthRole",
      "AuthRoleArn": "arn:aws:iam::086143043656:role/amplify-gsg-web-dev-authRole",
      "UnauthRoleArn": "arn:aws:iam::086143043656:role/amplify-gsg-web-dev-unauthRole",
      "Region": "us-east-1"
    }
  }
}
```

### Key Security Features:
- **IAM Roles**: Separate auth/unauth roles for controlled access
- **Environment Variables**: Secure storage in Amplify Console
- **HTTPS**: Enforced SSL/TLS for all traffic
- **JWT Authentication**: Integration with AWS Cognito

---

## 📊 Cost Optimization Strategy

### Current Operational Costs: ~$20-25/month
- **Amplify Hosting**: ~$15/month (build minutes + storage)
- **DynamoDB**: ~$2-5/month (pay-per-request)
- **Lambda**: ~$1-3/month (event-driven execution)
- **S3 Storage**: ~$1-2/month (with lifecycle policies)

### Cost Control Measures:
1. **Pay-per-request DynamoDB**: Only pay for actual usage
2. **Amplify caching**: Reduces build times and costs
3. **Lambda optimization**: Efficient memory allocation
4. **S3 lifecycle policies**: Automated cost management

---

## 🎯 Future Deployment Templates

### Template for New Next.js App:
```bash
#!/bin/bash
# Deploy new Next.js app in Continuum Overworld monorepo

APP_NAME="$1"
VERSION="${2:-v1.0.0}"

# Create directory structure
mkdir -p "Agora/App--${APP_NAME}__PROD@${VERSION}"
cd "Agora/App--${APP_NAME}__PROD@${VERSION}"

# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Update root amplify.yml paths
sed -i "s/Site--GreenStemGlobal__PROD@v1.0.0/App--${APP_NAME}__PROD@${VERSION}/g" ../../amplify.yml

echo "✅ New app ${APP_NAME} ready for deployment"
echo "📋 Next steps:"
echo "1. Configure environment variables in Amplify Console"
echo "2. Test local build: npm run build"
echo "3. Commit and push to trigger deployment"
```

---

## 🏆 Success Criteria Checklist

Before deployment, ensure:
- [ ] Root `amplify.yml` has correct app directory path
- [ ] Single `cd` command in preBuild phase only
- [ ] Artifact `baseDirectory` points to app's `.next` folder
- [ ] Cache paths point to app's `node_modules`
- [ ] Commit message contains no special characters
- [ ] Environment variables configured in Amplify Console
- [ ] Local build passes: `npm run build`
- [ ] Package.json has required dependencies
- [ ] TypeScript configuration excludes unnecessary directories

---

**Document Version**: 2.0  
**Last Verified**: September 2025  
**Deployment Status**: ✅ Production Ready  
**Team Contact**: Development Team via GitHub Issues

---

*This blueprint is the definitive guide for deploying applications within the Continuum Overworld monorepo architecture. Follow these specifications exactly to ensure deployment success.*