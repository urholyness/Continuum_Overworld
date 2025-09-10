# GSG Validation (Sandbox)
Prereqs: AWS CLI v2, jq, curl, Node 20

1) cp .env.sample .env && fill values
2) make validate       # runs smoke + API + E2E
3) make alerts         # optional: fire test alert

Exit code != 0 means fail. Do not approve PR until green.

## Prerequisites

- AWS CLI v2 configured with appropriate credentials
- `jq` for JSON parsing
- `curl` for HTTP requests
- Node.js 20+ for E2E testing
- `newman` for Postman collection testing

## Environment Setup

Copy the sample environment file and fill in your actual values:

```bash
cp .env.sample .env
# Edit .env with your actual credentials
```

## Running Tests

### Full Validation Suite
```bash
make validate
```

### Individual Test Categories
```bash
make smoke    # AWS infrastructure checks
make api      # API endpoint validation
make e2e      # End-to-end UI testing
make alerts   # Test alert system
```

## What Gets Tested

### Smoke Tests
- DynamoDB readings exist for today
- NDVI tiles present in S3

### API Tests
- Farm summary endpoint
- Readings stream endpoint
- Operations CRUD endpoints
- Postman collection validation

### E2E Tests
- Farm page loads correctly
- NDVI thumbnail displays
- Weather freshness indicator
- Farm map renders

## GitHub Actions

The validation runs automatically on PRs to the `sandbox` branch. Required secrets:

- `AWS_VALIDATOR_ROLE_ARN`: IAM role for AWS access
- `API_BASE`: Sandbox API base URL
- `UI_BASE`: Sandbox UI base URL
- `ADMIN_JWT`: Admin authentication token

## Troubleshooting

- Check AWS credentials and permissions
- Verify environment variables are set
- Ensure all required tools are installed
- Check network connectivity to sandbox endpoints




