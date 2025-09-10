#!/bin/bash

# Environment Switcher for Helios Console
# Usage: ./switch-env.sh demo|real [api-url] [user-pool-id] [client-id]

set -e

ENV_MODE=${1:-demo}
API_URL=${2:-"https://cn-dev-api.greenstemglobal.com"}
USER_POOL_ID=${3:-"us-east-1_PLACEHOLDER"}  
CLIENT_ID=${4:-"PLACEHOLDER_CLIENT_ID"}

ENV_FILE=".env.development.local"

if [ "$ENV_MODE" = "demo" ]; then
    echo "🎭 Switching to DEMO mode..."
    cat > $ENV_FILE << EOF
# Development environment variables - DEMO MODE
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
NEXT_PUBLIC_WS_URL=wss://ws-dev.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111

# Cognito configuration (placeholders in demo mode)
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/$USER_POOL_ID
AUTH_CLIENT_ID=$CLIENT_ID
AUTH_AUDIENCE=$CLIENT_ID

# DEMO MODE ENABLED
NEXT_PUBLIC_DEMO_MODE=true

# Development settings
API_INTERNAL_TOKEN=dev-internal-token
ETH_RPC_URL=https://sepolia.infura.io/v3/dev-project-id
JWT_SECRET=dev-jwt-secret-key
EOF

    echo "✅ Switched to DEMO mode"
    echo "   - Using demo data"
    echo "   - No API calls to real endpoints"
    echo "   - Restart dev server: npm run dev"

elif [ "$ENV_MODE" = "real" ]; then
    if [ "$USER_POOL_ID" = "us-east-1_PLACEHOLDER" ] || [ "$CLIENT_ID" = "PLACEHOLDER_CLIENT_ID" ]; then
        echo "❌ Error: You must provide real API URL, User Pool ID, and Client ID"
        echo "Usage: ./switch-env.sh real <api-url> <user-pool-id> <client-id>"
        echo ""
        echo "Example:"
        echo "./switch-env.sh real https://cn-dev-api.greenstemglobal.com us-east-1_ABC123DEF 4h8k2m9n5p7q1r3s6t"
        exit 1
    fi

    echo "🚀 Switching to REAL API mode..."
    cat > $ENV_FILE << EOF
# Development environment variables - REAL APIs
NEXT_PUBLIC_SITE_ENV=development
NEXT_PUBLIC_API_BASE_URL=$API_URL
NEXT_PUBLIC_WS_URL=wss://ws-dev.greenstemglobal.com
NEXT_PUBLIC_CHAIN_ID=11155111

# Real Cognito configuration
AUTH_ISSUER=https://cognito-idp.us-east-1.amazonaws.com/$USER_POOL_ID
AUTH_CLIENT_ID=$CLIENT_ID
AUTH_AUDIENCE=$CLIENT_ID

# REAL API MODE ENABLED
NEXT_PUBLIC_DEMO_MODE=false

# Development settings
API_INTERNAL_TOKEN=dev-internal-token
ETH_RPC_URL=https://sepolia.infura.io/v3/dev-project-id
JWT_SECRET=dev-jwt-secret-key
EOF

    echo "✅ Switched to REAL API mode"
    echo "   - API URL: $API_URL"
    echo "   - User Pool: $USER_POOL_ID"
    echo "   - Client ID: $CLIENT_ID"
    echo "   - Restart dev server: npm run dev"

else
    echo "❌ Error: Invalid mode. Use 'demo' or 'real'"
    echo "Usage: ./switch-env.sh demo|real [api-url] [user-pool-id] [client-id]"
    exit 1
fi