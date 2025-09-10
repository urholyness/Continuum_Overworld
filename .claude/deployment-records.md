# Claude Code Deployment Records

## Future Deployment Reference

This file contains critical information for future deployments from the root folder of Continuum_Overworld.

### ✅ PROVEN DEPLOYMENT PATTERN

**Root Amplify Configuration** (`/amplify.yml`):
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

### 🚨 CRITICAL RULES FOR SUCCESS

1. **Single CD Command**: Only use `cd` in preBuild phase, never in build phase
2. **Directory Context**: Build phase inherits directory from preBuild
3. **Artifact Paths**: Must point to subdirectory `.next` folder
4. **Safe Commit Messages**: Never use colons (:), pipes (|), or special characters
5. **Cache Strategy**: Cache at app level, not root level

### 📁 MONOREPO STRUCTURE PATTERN

For any new app deployment:
```bash
# 1. Create app directory
mkdir -p Agora/App--{NAME}__PROD@v{VERSION}

# 2. Update root amplify.yml paths
# Change: Agora/Site--GreenStemGlobal__PROD@v1.0.0
# To: Agora/App--{NAME}__PROD@v{VERSION}

# 3. Initialize Next.js in app directory
cd Agora/App--{NAME}__PROD@v{VERSION}
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# 4. Test build locally
npm run build

# 5. Commit with safe message
git add .
git commit -m "Add {NAME} production app deployment"
git push origin main
```

### 🏗️ CURRENT PRODUCTION STATUS

**App**: Site--GreenStemGlobal__PROD@v1.0.0
**Status**: ✅ Successfully Deployed
**Amplify App ID**: dgcik29wowtkc  
**Region**: us-east-1
**Monthly Cost**: ~$20-25
**Last Verified**: September 2025

### 🔧 TROUBLESHOOTING REFERENCE

| Issue | Solution |
|-------|----------|
| Build fails with "cd" error | Check for duplicate cd commands |
| Git index lock | `rm -f .git/index.lock` |
| npm timeouts | Use workspace-free configuration |
| Commit breaks deploy | Check for special characters |

### 📚 DOCUMENTATION CREATED

1. **DEPLOYMENT-BLUEPRINT.md** - Complete deployment guide
2. **DEPLOYMENT-SPECS.md** - Technical specifications
3. **TEAM-HANDOFF.md** - Operational procedures
4. **CONTRIBUTING.md** - Git workflow rules

These documents contain the complete knowledge base for maintaining and expanding the deployment architecture.

---

**Created**: September 2025  
**Status**: Production Ready  
**Verified**: Deployment successful and operational