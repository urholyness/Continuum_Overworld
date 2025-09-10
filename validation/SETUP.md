# GSG Validation Framework Setup

## Overview
This validation framework provides comprehensive testing for the GSG sandbox environment, including:
- **Smoke Tests**: AWS infrastructure validation
- **API Tests**: REST endpoint testing with Postman
- **E2E Tests**: UI testing with Playwright
- **Alert Tests**: Event-driven system validation

## Quick Start

### 1. Environment Configuration
```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env with your actual credentials
# - AWS credentials and region
# - API endpoints
# - Admin JWT token
# - Farm configuration
```

### 2. Install Prerequisites
```bash
# Required tools
- AWS CLI v2
- jq (JSON processor)
- curl
- Node.js 20+
- newman (Postman CLI)

# Windows (with Chocolatey)
choco install awscli jq curl nodejs

# Install newman globally
npm install -g newman
```

### 3. Run Validation
```bash
# Full validation suite
make validate

# Individual test categories
make smoke    # AWS checks
make api      # API validation
make e2e      # UI testing
make alerts   # Alert system
```

## File Structure

```
validation/
├── .env.sample          # Environment template
├── Makefile            # Build commands
├── README.md           # Usage documentation
├── SETUP.md            # This file
├── .github/
│   └── workflows/
│       └── validate-sbx.yml  # CI/CD pipeline
├── e2e/                # End-to-end tests
│   ├── package.json
│   ├── playwright.config.ts
│   └── tests/
│       └── e2e.spec.ts
├── postman/            # API testing
│   ├── gsg-farm-api.postman_collection.json
│   └── gsg-env.postman_environment.json
└── scripts/            # Bash test scripts
    ├── check_dynamo_readings.sh
    ├── check_s3_ndvi.sh
    ├── get_summary.sh
    ├── get_readings_since.sh
    ├── post_ops_event.sh
    ├── get_ops_list.sh
    └── trigger_ndvi_drop_event.sh
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for resources | `eu-central-1` |
| `AWS_PROFILE` | AWS credentials profile | `gsg-sbx` |
| `READINGS_TABLE` | DynamoDB table name | `readings` |
| `CURATED_BUCKET` | S3 bucket for curated data | `gsg-data-curated` |
| `FARM_ID` | Target farm identifier | `2BH` |
| `FARM_DATE_UTC` | Date for NDVI validation | `2025-08-31` |
| `API_BASE` | Base URL for API endpoints | `https://api.sbx.greenstemglobal.de` |
| `ADMIN_JWT` | Admin authentication token | `eyJ...` |
| `UI_BASE` | Base URL for UI testing | `https://app.sbx.greenstemglobal.de` |

## IAM Permissions Required

The validation framework requires these AWS permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "s3:ListBucket",
        "s3:GetObject",
        "events:PutEvents",
        "execute-api:Invoke"
      ],
      "Resource": "*"
    }
  ]
}
```

## GitHub Actions Integration

The framework automatically runs on PRs to the `sandbox` branch. Required repository secrets:

- `AWS_VALIDATOR_ROLE_ARN`: IAM role for AWS access
- `API_BASE`: Sandbox API base URL
- `UI_BASE`: Sandbox UI base URL
- `ADMIN_JWT`: Admin authentication token

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Ensure AWS CLI is configured with correct profile
2. **Environment Variables**: Check all required variables are set in `.env`
3. **Network Access**: Verify connectivity to sandbox endpoints
4. **Tool Installation**: Ensure all prerequisites are installed and in PATH

### Debug Mode

Run individual scripts with verbose output:
```bash
bash -x scripts/check_dynamo_readings.sh
```

### Manual Testing

Test individual components:
```bash
# Test AWS connectivity
aws sts get-caller-identity

# Test API endpoints
curl -v "${API_BASE}/farms/2BH/summary"

# Test UI access
curl -v "${UI_BASE}/farms/2BH"
```

## Next Steps

1. Configure your `.env` file with actual credentials
2. Test individual components before running full validation
3. Set up GitHub Actions secrets for CI/CD
4. Integrate with your development workflow

## Support

For issues or questions:
- Check the main README.md
- Review script output for error details
- Verify environment configuration
- Test individual components in isolation




