#!/bin/bash
set -e

echo "🔐 Creating C_N IAM Roles with Least Privilege..."

ROLE_NAME="C_N-Lambda-Execution-Role"

# Check if role exists
if aws iam get-role --role-name "$ROLE_NAME" 2>/dev/null; then
    echo "  ✓ Role $ROLE_NAME exists"
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
else
    # Create the role
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' \
        --tags "Key=Environment,Value=C_N" "Key=Component,Value=Lambda" "Key=Division,Value=Aegis"
    
    # Attach only basic execution role (CloudWatch logs)
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
    echo "  ✓ Created role: $ROLE_NAME"
fi

# Create scoped inline policy for specific resources only
echo "  Adding scoped permissions..."
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "C_N-Lambda-Scoped" \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["dynamodb:PutItem"],
                "Resource": [
                    "arn:aws:dynamodb:*:*:table/C_N-FarmMetrics-Live",
                    "arn:aws:dynamodb:*:*:table/C_N-Pantheon-Registry"
                ]
            },
            {
                "Effect": "Allow",
                "Action": ["events:PutEvents"],
                "Resource": "arn:aws:events:*:*:event-bus/C_N-EventBus-Core"
            }
        ]
    }'

echo "  ✓ Applied least-privilege policy"

# Save role ARN for Lambda deployments
echo "$ROLE_ARN" > /mnt/c/users/password/continuum_Overworld/.lambda_role_arn

echo "✅ IAM roles configured with least privilege"