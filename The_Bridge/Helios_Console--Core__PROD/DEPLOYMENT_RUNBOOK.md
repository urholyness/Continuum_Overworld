# Helios Console Deployment Runbook

## Pre-Deployment Checklist

### Local Development Testing
1. **Environment Setup**
   ```bash
   cp .env.example .env.development.local
   # Configure with DEV API endpoints
   npm ci
   ```

2. **Quality Gates**
   ```bash
   npm run typecheck  # TypeScript compilation
   npm run lint       # ESLint validation
   npm test          # Unit tests
   npm run build     # Production build test
   npm run e2e       # End-to-end tests (optional)
   ```

3. **API Connectivity Test**
   ```bash
   npm run dev
   # Navigate to http://localhost:3000
   # Verify all four pages load without errors:
   # - /ops (operations metrics)
   # - /trace (traceability events) 
   # - /agents (agent status)
   # - /admin/farms (farm management)
   ```

### Backend Readiness Verification
```bash
# Test Composer API
curl -H "Authorization: Bearer $DEV_JWT" \
  "$DEV_API_URL/composer/ops/metrics?org=org-main"

# Test Admin API  
curl -H "Authorization: Bearer $ADMIN_JWT" \
  "$DEV_API_URL/admin/farms"

# Verify response format matches Zod schemas
```

## Deployment Process

### Branch Strategy
- `dev` → DEV environment
- `stage` → STAGE environment  
- `main` → PROD environment

### Step 1: Development Deployment
```bash
git checkout dev
git pull origin dev

# Make changes and test locally
npm run typecheck && npm run lint && npm test

git add .
git commit -m "Add feature xyz with API integration"
git push origin dev
```

**Amplify automatically deploys to DEV environment**

### Step 2: Staging Deployment
```bash
git checkout stage
git merge dev
git push origin stage
```

**Amplify automatically deploys to STAGE environment**

### Step 3: Production Deployment
```bash
git checkout main
git merge stage
git push origin main
```

**Amplify automatically deploys to PROD environment**

## Environment Configuration

### Amplify Console Settings

**DEV Environment (`dev` branch):**
```bash
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://api-dev.cn.example.com
NEXT_PUBLIC_WS_URL=wss://ws-dev.cn.example.com
NEXT_PUBLIC_CHAIN_ID=11155111
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/dev-pool
AUTH_CLIENT_ID=dev-client-id
AUTH_AUDIENCE=dev-api-audience  
JWT_SECRET=[SECURE-DEV-SECRET]
```

**STAGE Environment (`stage` branch):**
```bash
NEXT_PUBLIC_SITE_ENV=stage
NEXT_PUBLIC_API_BASE_URL=https://api-stage.cn.example.com
NEXT_PUBLIC_WS_URL=wss://ws-stage.cn.example.com
NEXT_PUBLIC_CHAIN_ID=11155111
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/stage-pool
AUTH_CLIENT_ID=stage-client-id
AUTH_AUDIENCE=stage-api-audience
JWT_SECRET=[SECURE-STAGE-SECRET]
```

**PROD Environment (`main` branch):**
```bash
NEXT_PUBLIC_SITE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://api.cn.example.com
NEXT_PUBLIC_WS_URL=wss://ws.cn.example.com
NEXT_PUBLIC_CHAIN_ID=11155111
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/prod-pool
AUTH_CLIENT_ID=prod-client-id
AUTH_AUDIENCE=prod-api-audience
JWT_SECRET=[SECURE-PROD-SECRET]
```

## Post-Deployment Verification

### Automated Checks (CI/CD Pipeline)
```bash
# Health check endpoint
curl -f $DEPLOYED_URL/api/health || exit 1

# Page load tests
curl -f $DEPLOYED_URL/ || exit 1
curl -f $DEPLOYED_URL/ops || exit 1
curl -f $DEPLOYED_URL/trace || exit 1
curl -f $DEPLOYED_URL/agents || exit 1
curl -f $DEPLOYED_URL/admin/farms || exit 1
```

### Manual Verification
1. **Functional Testing**
   - Navigate to each page: `/ops`, `/trace`, `/agents`, `/admin/farms`
   - Verify data loads correctly (no schema validation errors)
   - Check authentication redirects work
   - Test role-based access control

2. **Performance Testing**
   ```bash
   # Lighthouse CI check (if configured)
   npx lighthouse-ci autorun

   # Core Web Vitals targets:
   # - LCP < 2.5s
   # - CLS < 0.1
   # - FID < 100ms
   ```

3. **Security Validation**
   - Verify CSP headers are applied
   - Check HTTPS enforcement
   - Test unauthorized access returns 403/401

## Rollback Procedures

### Immediate Rollback (Amplify Console)
1. Navigate to AWS Amplify Console
2. Select Helios Console app
3. Go to affected branch/environment
4. Click "Redeploy" on previous successful build

### Git-Based Rollback
```bash
# Find last good commit
git log --oneline -10

# Revert problematic commit
git revert <bad-commit-hash>
git push origin <branch>

# Or reset to previous state (destructive)
git reset --hard <good-commit-hash>
git push --force origin <branch>
```

## Monitoring & Alerting

### Application Metrics
- **Amplify Console**: Build status, deployment metrics
- **CloudWatch**: Error rates, response times
- **Real User Monitoring**: Core Web Vitals, user flows

### Key Alerts
- Build failure notifications
- API error rate > 5%
- Page load time > 3 seconds
- Authentication failure spikes

### Log Locations
- **Build logs**: Amplify Console → Build history
- **Runtime logs**: CloudWatch Logs → `/aws/amplify/apps/{app-id}`
- **Frontend errors**: Browser dev tools, user reporting

## Troubleshooting

### Common Build Issues
1. **TypeScript Errors**
   ```bash
   npm run typecheck
   # Fix reported issues
   ```

2. **Dependency Issues**
   ```bash
   rm -rf node_modules package-lock.json
   npm ci
   npm run build
   ```

3. **Environment Variable Issues**
   - Check Amplify Console environment variables
   - Ensure `NEXT_PUBLIC_*` variables are properly prefixed
   - Verify sensitive variables are not exposed

### Runtime Issues
1. **API Connection Failures**
   - Verify API endpoints are accessible
   - Check CORS configuration
   - Validate JWT tokens and permissions

2. **Authentication Problems**
   - Check Cognito configuration
   - Verify JWT issuer and client settings
   - Test role assignments

3. **Performance Issues**
   - Check API response times
   - Verify caching configuration
   - Monitor Core Web Vitals

### Emergency Contacts
- **Technical Issues**: DevOps Team
- **Business Impact**: Product Owner
- **Security Incidents**: Security Team
- **AWS Support**: Business Support Plan

## Maintenance Windows

### Scheduled Maintenance
- **DEV**: Anytime (development environment)
- **STAGE**: Business hours (testing environment)  
- **PROD**: Outside business hours with advance notice

### Release Schedule
- **Hotfixes**: As needed (emergency patches)
- **Minor releases**: Weekly (feature additions)
- **Major releases**: Monthly (breaking changes)

### Backup & Recovery
- **Code**: Git repository (multiple remotes)
- **Configuration**: Environment variables documented
- **Dependencies**: package-lock.json committed
- **Deployment**: Amplify build history (90 days)

## Cost Monitoring

### Monthly Budget Targets
- **DEV**: $10-15 (development usage)
- **STAGE**: $15-25 (staging testing)
- **PROD**: $25-40 (production traffic)

### Cost Optimization
- Optimize build cache usage
- Monitor bandwidth consumption  
- Review and cleanup old deployments
- Use appropriate instance sizes

---

**Document Version**: 1.0  
**Last Updated**: September 2025  
**Maintainer**: DevOps Team