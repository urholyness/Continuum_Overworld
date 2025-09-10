#!/bin/bash
# Test Cases for Task 1: Website Real Data Connection

echo "====================================="
echo "Task 1: Website Real Data Connection"
echo "Test Suite"
echo "====================================="

API_BASE="https://cn-api.greenstemglobal.com"

# Test 1: Valid trace ID
echo -e "\n[TEST 1] Testing valid trace ID..."
curl -X GET "$API_BASE/public/trace/LOT-2024-FB-001" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

# Test 2: Highlights endpoint
echo -e "\n[TEST 2] Testing highlights endpoint..."
curl -X GET "$API_BASE/public/trace/highlights" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

# Test 3: Invalid trace ID (404 handling)
echo -e "\n[TEST 3] Testing 404 handling..."
curl -X GET "$API_BASE/public/trace/INVALID-LOT-ID" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

# Test 4: Response time check
echo -e "\n[TEST 4] Testing response time..."
time curl -X GET "$API_BASE/public/trace/highlights" \
  -H "Content-Type: application/json" \
  -o /dev/null -s -w "Time: %{time_total}s\n"

# Test 5: Data structure validation
echo -e "\n[TEST 5] Validating response structure..."
response=$(curl -s "$API_BASE/public/trace/LOT-2024-FB-001")
if echo "$response" | grep -q '"lotNumber"'; then
  echo "✓ lotNumber field present"
fi
if echo "$response" | grep -q '"farmName"'; then
  echo "✓ farmName field present"
fi
if echo "$response" | grep -q '"product"'; then
  echo "✓ product field present"
fi
if echo "$response" | grep -q '"timeline"'; then
  echo "✓ timeline field present"
fi

echo -e "\n====================================="
echo "Test suite completed"
echo "====================================="
