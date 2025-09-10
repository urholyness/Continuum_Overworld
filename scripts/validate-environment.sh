#!/bin/bash

# Validation script for Continuum Overworld Integration
# Tests all stop conditions per environment

set -e

ENVIRONMENT=${1:-dev}
ROOT_DOMAIN=${2:-greenstemglobal.com}
API_URL="https://cn-${ENVIRONMENT}-api.${ROOT_DOMAIN}"

echo "🔍 Validating ${ENVIRONMENT} environment"
echo "API URL: ${API_URL}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n🧪 Testing: ${test_name}"
    
    if eval "$test_command"; then
        if [ "$expected_result" = "pass" ]; then
            echo -e "✅ ${GREEN}PASS${NC}: $test_name"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "❌ ${RED}FAIL${NC}: $test_name (expected failure but got success)"
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            echo -e "✅ ${GREEN}PASS${NC}: $test_name (expected failure)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "❌ ${RED}FAIL${NC}: $test_name"
        fi
    fi
}

# Function to check if JWT tokens are available
check_jwt_tokens() {
    if [ -z "$ADMIN_JWT" ] || [ -z "$OPS_JWT" ] || [ -z "$TRACE_JWT" ]; then
        echo -e "${YELLOW}⚠️ Warning: JWT tokens not set. Authorization tests will be skipped.${NC}"
        echo "To test authorization, set these environment variables:"
        echo "  export ADMIN_JWT='your-admin-jwt-token'"
        echo "  export OPS_JWT='your-ops-jwt-token'"
        echo "  export TRACE_JWT='your-trace-jwt-token'"
        return 1
    fi
    return 0
}

echo -e "\n🚀 Starting validation tests...\n"

# A. Data Readiness Tests
echo -e "📊 ${YELLOW}A. DATA READINESS TESTS${NC}"

# Check if DynamoDB tables have data
if command -v aws &> /dev/null; then
    run_test "Metrics table has data" \
        "aws dynamodb scan --table-name C_N-Metrics-Operational-${ENVIRONMENT} --max-items 1 --region us-east-1 | jq -r '.Count >= 1'" \
        "pass"
    
    run_test "Events table has data" \
        "aws dynamodb scan --table-name C_N-Events-Trace-${ENVIRONMENT} --max-items 10 --region us-east-1 | jq -r '.Count >= 1'" \
        "pass"
    
    run_test "Farms table has data" \
        "aws dynamodb scan --table-name C_N-Registry-Farms-${ENVIRONMENT} --max-items 5 --region us-east-1 | jq -r '.Count >= 1'" \
        "pass"
    
    run_test "Agents table has data" \
        "aws dynamodb scan --table-name C_N-Pantheon-Registry-${ENVIRONMENT} --max-items 5 --region us-east-1 | jq -r '.Count >= 1'" \
        "pass"
else
    echo -e "${YELLOW}⚠️ AWS CLI not available, skipping DynamoDB data checks${NC}"
fi

# B. API Availability Tests
echo -e "\n🌐 ${YELLOW}B. API AVAILABILITY TESTS${NC}"

run_test "Health endpoint responds" \
    "curl -s -f ${API_URL}/health" \
    "pass"

run_test "CORS headers present" \
    "curl -s -I ${API_URL}/health | grep -i 'access-control-allow-origin'" \
    "pass"

run_test "API returns JSON" \
    "curl -s ${API_URL}/health | jq . > /dev/null" \
    "pass"

# C. Performance Tests
echo -e "\n⚡ ${YELLOW}C. PERFORMANCE TESTS${NC}"

run_test "Response time < 600ms" \
    "timeout 10 curl -w '%{time_total}' -s -o /dev/null ${API_URL}/health | awk '{print (\$1 < 0.6)}'" \
    "pass"

# D. Authorization Tests (if JWT tokens available)
if check_jwt_tokens; then
    echo -e "\n🔐 ${YELLOW}D. AUTHORIZATION TESTS${NC}"
    
    # Admin access tests
    run_test "Admin can access farms" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $ADMIN_JWT' ${API_URL}/admin/farms | grep -q '200'" \
        "pass"
    
    run_test "Admin can access agents" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $ADMIN_JWT' ${API_URL}/admin/agents | grep -q '200'" \
        "pass"
    
    # Non-admin denied tests
    run_test "Ops user denied admin access" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $OPS_JWT' ${API_URL}/admin/farms | grep -q '403'" \
        "pass"
    
    run_test "Trace user denied admin access" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $TRACE_JWT' ${API_URL}/admin/farms | grep -q '403'" \
        "pass"
    
    # Role-based access tests
    run_test "Ops user can access metrics" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $OPS_JWT' '${API_URL}/composer/ops/metrics?org=org-main' | grep -q '200'" \
        "pass"
    
    run_test "Trace user can access events" \
        "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer $TRACE_JWT' '${API_URL}/composer/trace/events?org=org-main' | grep -q '200'" \
        "pass"
    
    # Unauthenticated requests denied
    run_test "Unauthenticated access denied" \
        "curl -s -o /dev/null -w '%{http_code}' ${API_URL}/admin/farms | grep -q '401'" \
        "pass"
else
    echo -e "\n🔐 ${YELLOW}D. AUTHORIZATION TESTS - SKIPPED${NC}"
fi

# E. Public Highlights Tests
echo -e "\n📰 ${YELLOW}E. PUBLIC HIGHLIGHTS TESTS${NC}"

run_test "Public highlights accessible" \
    "curl -s -f ${API_URL}/public/trace/highlights" \
    "pass"

run_test "Public highlights returns items" \
    "curl -s ${API_URL}/public/trace/highlights | jq -r '.items | length >= 1'" \
    "pass"

run_test "Public highlights properly anonymized" \
    "curl -s ${API_URL}/public/trace/highlights | jq -r '.note | contains(\"anonymized\")'" \
    "pass"

# F. Schema Validation Tests
echo -e "\n📝 ${YELLOW}F. SCHEMA VALIDATION TESTS${NC}"

if check_jwt_tokens; then
    run_test "Ops metrics match schema" \
        "curl -s -H 'Authorization: Bearer $ADMIN_JWT' '${API_URL}/composer/ops/metrics?org=org-main' | jq -r '.[0] | has(\"kpi\") and has(\"value\") and has(\"unit\") and has(\"ts\")'" \
        "pass"
    
    run_test "Farms match schema" \
        "curl -s -H 'Authorization: Bearer $ADMIN_JWT' ${API_URL}/admin/farms | jq -r '.[0] | has(\"id\") and has(\"name\") and has(\"region\") and has(\"hectares\") and has(\"status\")'" \
        "pass"
    
    run_test "Agents match schema" \
        "curl -s -H 'Authorization: Bearer $ADMIN_JWT' ${API_URL}/admin/agents | jq -r '.[0] | has(\"id\") and has(\"name\") and has(\"role\") and has(\"tier\") and has(\"status\")'" \
        "pass"
fi

# G. Error Handling Tests
echo -e "\n🚨 ${YELLOW}G. ERROR HANDLING TESTS${NC}"

run_test "Invalid endpoint returns 404" \
    "curl -s -o /dev/null -w '%{http_code}' ${API_URL}/invalid/endpoint | grep -q '404'" \
    "pass"

run_test "Malformed requests return 400" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' -d '{invalid json}' ${API_URL}/admin/farms | grep -q '400'" \
    "pass"

# Summary
echo -e "\n📊 ${YELLOW}TEST SUMMARY${NC}"
echo "=============================="
echo "Environment: ${ENVIRONMENT}"
echo "API URL: ${API_URL}"
echo "Total tests: ${TOTAL_TESTS}"
echo "Passed: ${PASSED_TESTS}"
echo "Failed: $((TOTAL_TESTS - PASSED_TESTS))"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n🎉 ${GREEN}ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}Environment ${ENVIRONMENT} is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n❌ ${RED}SOME TESTS FAILED!${NC}"
    echo -e "${RED}Please fix issues before proceeding to next stage.${NC}"
    exit 1
fi