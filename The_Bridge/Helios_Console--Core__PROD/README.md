# Helios Console - Core Production v1.0.1

## Overview

Helios Console is the central web interface for the Continuum Overworld Enterprise Agricultural Data Platform. It provides real-time monitoring, traceability, and administrative capabilities for farm operations, agent management, and system oversight.

## Features

- **Operations Dashboard** (`/ops`): Real-time operational metrics and KPIs
- **Traceability Interface** (`/trace`): Event audit trails and tracking
- **Agent Management** (`/agents`): Monitor agent status and performance
- **Farm Administration** (`/admin/farms`): Manage farm registrations and configurations

## Technology Stack

- **Framework**: Next.js 14 (App Router, TypeScript)
- **Styling**: Tailwind CSS + shadcn/ui
- **Validation**: Zod runtime validation
- **Authentication**: JWT/Cognito with role-based access control
- **Testing**: Jest (unit tests) + Playwright (E2E tests)
- **Deployment**: AWS Amplify with branch-based environments

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- npm or yarn
- Access to Composer and Admin API endpoints

### Installation

```bash
# Install dependencies
npm ci

# Copy and configure environment variables
cp .env.example .env.development.local
# Edit .env.development.local with your API endpoints and credentials

# Run development server
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_SITE_ENV` | Environment identifier | `development`, `stage`, `production` |
| `NEXT_PUBLIC_API_BASE_URL` | Base URL for API endpoints | `https://api-dev.example.com` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL for real-time updates | `wss://ws-dev.example.com` |
| `AUTH_ISSUER` | Cognito issuer URL | `https://cognito-idp.region.amazonaws.com/poolId` |
| `AUTH_CLIENT_ID` | Cognito client ID | `your-client-id` |
| `JWT_SECRET` | JWT signing secret (server-side) | `your-secret-key` |

## Available Scripts

- `npm run dev` - Start development server on port 3000
- `npm run build` - Build production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript compiler check
- `npm test` - Run unit tests
- `npm run e2e` - Run end-to-end tests

## API Integration

### Composer API Endpoints

- `GET /composer/ops/metrics` - Operational KPIs
- `GET /composer/trace/events` - Traceability events

### Admin API Endpoints

- `GET /admin/farms` - List farms
- `POST /admin/farms` - Create/update farm
- `GET /admin/agents` - List agents

All API calls include:
- Automatic JWT authentication
- Request/response logging
- Zod schema validation
- Error handling with user-friendly messages

## Authentication & Authorization

The application uses JWT-based authentication with role-based access control:

- **Public Routes**: Home page, login
- **Authenticated Routes**: `/ops`, `/trace`, `/agents`
- **Admin Routes**: `/admin/*` (requires `admin` role)

Roles are derived from JWT claims (`cognito:groups`):
- `ops` - Operations dashboard access
- `trace` - Traceability interface access
- `admin` - Full administrative access

## Testing

### Unit Tests

```bash
npm test
```

Unit tests cover:
- API client functions
- Schema validation
- Authentication utilities
- Component rendering

### End-to-End Tests

```bash
npm run e2e
```

E2E tests verify:
- Page navigation
- Content rendering
- Authentication flows
- Error handling

## Deployment

### Branch-Based Environments

| Branch | Environment | Domain |
|--------|-------------|---------|
| `dev` | Development | `https://dev.helios-console.amplifyapp.com` |
| `stage` | Staging | `https://stage.helios-console.amplifyapp.com` |
| `main` | Production | `https://helios-console.amplifyapp.com` |

### AWS Amplify Configuration

The `amplify.yml` file configures the build process:

```yaml
version: 1
applications:
  - appRoot: .
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
          - .next/cache/**/*
```

Environment variables are configured per-branch in the Amplify Console.

## Security

### Content Security Policy

The application includes comprehensive CSP headers:
- Scripts: Self + unsafe-eval/inline (Next.js requirement)
- Styles: Self + unsafe-inline
- Images: Self + data URIs + HTTPS
- Connections: Self + HTTPS/WSS APIs only
- Frame ancestors: None (clickjacking protection)

### Data Validation

All API responses are validated using Zod schemas:
- Runtime type checking
- Automatic error handling for malformed data
- Type safety throughout the application

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify `NEXT_PUBLIC_API_BASE_URL` is correct
   - Check network connectivity to API endpoints
   - Ensure JWT token is valid and not expired

2. **Build Failures**
   - Run `npm run typecheck` to identify TypeScript errors
   - Check for missing environment variables
   - Verify all dependencies are installed

3. **Authentication Issues**
   - Check Cognito configuration
   - Verify JWT secret and issuer settings
   - Ensure user has proper role assignments

### Debugging

Enable development logging by setting:
```bash
NODE_ENV=development
```

This will show:
- API request/response details
- Authentication flow information
- Error stack traces

## Architecture

```
src/
├── app/                    # Next.js App Router pages
│   ├── ops/               # Operations dashboard
│   ├── trace/             # Traceability interface
│   ├── agents/            # Agent monitoring
│   └── admin/farms/       # Farm administration
├── components/
│   └── ui/                # Reusable UI components
├── lib/
│   ├── api/               # API client and schemas
│   ├── auth/              # Authentication utilities
│   └── utils/             # Shared utilities
└── __tests__/             # Unit tests
```

## Contributing

1. Create feature branch from `dev`
2. Implement changes with tests
3. Ensure all quality gates pass:
   ```bash
   npm run typecheck
   npm run lint
   npm test
   npm run e2e
   ```
4. Submit pull request to `dev` branch

## Support

For technical issues:
- Check the troubleshooting section above
- Review application logs in AWS CloudWatch
- Create issue in repository with reproduction steps

For operational questions:
- Contact the DevOps team
- Check system status dashboard
- Review API documentation