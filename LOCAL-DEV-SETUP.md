# Local Development Setup Guide

## Quick Start - Helios Console

The Helios Console is ready for local development with demo data. Here's how to get it running:

### 1. Install Dependencies (Choose One Method)

#### Method A: Full Install (Recommended)
```bash
cd The_Bridge/Helios_Console--Core__PROD
npm install
```

#### Method B: Minimal Install (If full install fails)
```bash
cd The_Bridge/Helios_Console--Core__PROD
npm install --no-audit --production=false next react react-dom typescript
```

#### Method C: Use Yarn (Alternative)
```bash
cd The_Bridge/Helios_Console--Core__PROD
yarn install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at: http://localhost:3000

### 3. Demo Mode Features

The application is configured to run in demo mode (`NEXT_PUBLIC_DEMO_MODE=true`) with:

- **Ops Dashboard** (`/ops`): Real-time operational metrics with demo data
  - Throughput, efficiency, open orders
  - Cost per unit, uptime, queue depth
  - Auto-refreshing every 60 seconds

- **Trace Dashboard** (`/trace`): Supply chain trace events with demo data
  - Harvest, processing, logistics, blockchain events
  - Real-time event stream simulation

- **Admin > Farms** (`/admin/farms`): Farm management with demo data
  - 5 demo farms across Kenya counties
  - Active/paused status indicators
  - Farm details and hectare information

- **Agents Dashboard** (`/agents`): AI agent monitoring with demo data
  - 8 different agent types (processors, analyzers, oracles)
  - Online/degraded/offline status
  - T1/T2/T3 tier classifications

### 4. Environment Configuration

Current demo configuration in `.env.development.local`:
```bash
NEXT_PUBLIC_DEMO_MODE=true
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
```

### 5. Switching to Real APIs

When the backend is deployed, update `.env.development.local`:

1. Get the real API URL from CloudFormation outputs
2. Get Cognito User Pool ID and Client ID
3. Update the environment file:

```bash
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_API_BASE_URL=<real-api-url>
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>
AUTH_CLIENT_ID=<client-id>
```

### 6. Features in Demo Mode

#### Data Features:
- ✅ All 4 pages fully functional
- ✅ Realistic demo data that updates
- ✅ Zod schema validation
- ✅ Error handling and loading states
- ✅ Responsive design with Tailwind CSS
- ✅ shadcn/ui components

#### Authentication Features:
- 🔄 Demo auth bypass (no JWT required)
- ✅ Ready for Cognito integration
- ✅ Role-based access control structure

#### Performance Features:
- ✅ Next.js 14 App Router
- ✅ ISR caching (60-second revalidation)
- ✅ TypeScript strict mode
- ✅ ESLint + Prettier configured

### 7. Troubleshooting

#### If npm install fails:
```bash
# Clear cache
npm cache clean --force

# Try with legacy peer deps
npm install --legacy-peer-deps

# Or use yarn
yarn install
```

#### If development server won't start:
```bash
# Check Node.js version (requires 20.x)
node --version

# Try different port
npm run dev -- --port 3001
```

#### If pages show errors:
- Check browser console for detailed error messages
- Ensure demo data imports are working
- Verify environment variables are loaded

### 8. Next Steps

1. **✅ Local Demo**: Application runs with realistic demo data
2. **🔄 API Integration**: Deploy backend infrastructure using deployment scripts
3. **🔄 Authentication**: Connect to real Cognito User Pool
4. **🔄 Production**: Deploy to AWS Amplify with real environment variables

---

## Current Status

**✅ Ready for Local Development**
- All pages implemented and functional
- Demo data providing realistic user experience
- Environment configured for easy switching to real APIs
- Full TypeScript and modern React patterns

**🔄 Next: Deploy Backend Infrastructure**
- Use `/scripts/deploy-environment.sh` when SAM CLI is installed
- Follow `/DEPLOYMENT-MANUAL.md` for step-by-step instructions
- Update environment variables after deployment

---

**Document Version**: 1.0  
**Last Updated**: September 2025  
**Environment**: Local Development Ready