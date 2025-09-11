#!/bin/bash
set -e

echo "🏗️ Creating C_N S3 Data Lake in Frankfurt with Security Baseline..."

# Environment suffix and region configuration
ENV_SUFFIX="${ENVIRONMENT:-prod}"
TIERS=("raw" "bronze" "silver" "gold")
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
PROJECT_NAME="greenstemglobal"
AWS_REGION=${AWS_REGION:-eu-north-1}

for tier in "${TIERS[@]}"; do
    # S3 requires lowercase with environment suffix
    BUCKET_NAME="c-n-${PROJECT_NAME}-${tier}-${ENV_SUFFIX}"
    
    # Create bucket
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        echo "  ✓ Bucket $BUCKET_NAME exists"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION" \
            $(if [ "$AWS_REGION" != "us-east-1" ]; then echo "--create-bucket-configuration LocationConstraint=$AWS_REGION"; fi)
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled
        
        # Enable KMS encryption (Frankfurt security requirement)
        aws s3api put-bucket-encryption \
            --bucket "$BUCKET_NAME" \
            --server-side-encryption-configuration '{
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms",
                        "KMSMasterKeyID": "alias/aws/s3"
                    }
                }]
            }'
        
        # Block all public access
        aws s3api put-public-access-block \
            --bucket "$BUCKET_NAME" \
            --public-access-block-configuration '{
                "BlockPublicAcls":true,
                "IgnorePublicAcls":true,
                "BlockPublicPolicy":true,
                "RestrictPublicBuckets":true
            }'
        
        # Require TLS for all requests
        aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy "{
            \"Version\":\"2012-10-17\",
            \"Statement\":[{
                \"Sid\":\"DenyInsecureTransport\",
                \"Effect\":\"Deny\",
                \"Principal\":\"*\",
                \"Action\":\"s3:*\",
                \"Resource\":[
                    \"arn:aws:s3:::$BUCKET_NAME\",
                    \"arn:aws:s3:::$BUCKET_NAME/*\"
                ],
                \"Condition\":{\"Bool\":{\"aws:SecureTransport\":\"false\"}}
            }]
        }"
        
        # Add tags
        aws s3api put-bucket-tagging \
            --bucket "$BUCKET_NAME" \
            --tagging "TagSet=[{Key=Environment,Value=C_N},{Key=Tier,Value=$tier},{Key=Project,Value=$PROJECT_NAME},{Key=Division,Value=The_Bridge}]"
        
        echo "  ✓ Created $BUCKET_NAME with security baseline"
    fi
done

# Create lifecycle policy for intelligent tiering (gold tier only for long-term archives)
cat > /tmp/lifecycle-policy.json << 'POLICY'
{
    "Rules": [{
        "Id": "IntelligentTieringRule",
        "Status": "Enabled",
        "Transitions": [
            {"Days": 30, "StorageClass": "INTELLIGENT_TIERING"}
        ]
    }]
}
POLICY

# Apply lifecycle to gold tier only
aws s3api put-bucket-lifecycle-configuration \
    --bucket "c-n-${PROJECT_NAME}-gold-${ENV_SUFFIX}" \
    --lifecycle-configuration file:///tmp/lifecycle-policy.json

echo "✅ S3 Data Lake created with security baseline"