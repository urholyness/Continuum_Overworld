#!/bin/bash

echo "🧪 Testing C_N Infrastructure with Available Services..."

# Test S3 functionality
echo "  Testing S3 Data Lake..."
echo -n '{"test":"data","timestamp":'$(date +%s)'}' > /tmp/s3-test.json

# Upload test file to each tier
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
for tier in raw bronze silver gold; do
    BUCKET_NAME="c-n-greenstem-global-${tier}-${ACCOUNT_ID}"
    aws s3 cp /tmp/s3-test.json "s3://${BUCKET_NAME}/test/data.json" && \
    echo "    ✓ Upload to $tier tier successful" || \
    echo "    ✗ Upload to $tier tier failed"
done

# Test EventBridge
echo "  Testing EventBridge..."
aws events put-events \
    --entries '[{
        "Source": "Test.Infrastructure",
        "DetailType": "ConnectionTest",
        "Detail": "{\"test\": true, \"timestamp\": '$(date +%s)'}",
        "EventBusName": "C_N-EventBus-Core"
    }]' && echo "    ✓ EventBridge event sent successfully" || echo "    ✗ EventBridge test failed"

# Test SSM Parameter Store
echo "  Testing SSM Parameter Store..."
ENVIRONMENT=$(aws ssm get-parameter --name "/C_N/Config/Environment" --query 'Parameter.Value' --output text 2>/dev/null)
[ "$ENVIRONMENT" = "PROD" ] && echo "    ✓ SSM Parameter retrieval successful" || echo "    ✗ SSM Parameter test failed"

# List deployed resources
echo "  Verifying deployed resources..."

echo "    S3 Buckets:"
aws s3 ls | grep c-n- | awk '{print "      ✓ " $3}'

echo "    EventBridge Buses:"
aws events list-event-buses --query 'EventBuses[?starts_with(Name, `C_N`)].Name' --output text | tr '\t' '\n' | awk '{if($1) print "      ✓ " $1}'

echo "    EventBridge Rules:"
aws events list-rules --event-bus-name "C_N-EventBus-Core" --query 'Rules[].Name' --output text | tr '\t' '\n' | awk '{if($1) print "      ✓ " $1}'

echo "    SSM Parameters:"
aws ssm describe-parameters --parameter-filters "Key=Name,Option=BeginsWith,Values=/C_N/" --query 'Parameters[].Name' --output text | tr '\t' '\n' | awk '{if($1) print "      ✓ " $1}'

echo "
✅ Infrastructure tests complete for available services!
"