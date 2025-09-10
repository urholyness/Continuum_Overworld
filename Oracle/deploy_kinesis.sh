#!/bin/bash
set -e

echo "🌊 Creating C_N Kinesis Streams (1 shard each for cost optimization)..."

STREAMS=("FarmData" "SatelliteData" "LogisticsData" "BlockchainEvents")
PROJECT_NAME="greenstemglobal"
AWS_REGION=${AWS_REGION:-eu-central-1}
ENV_SUFFIX="${ENVIRONMENT:-prod}"

for stream in "${STREAMS[@]}"; do
    STREAM_NAME="C_N-${PROJECT_NAME}-${stream}-${ENV_SUFFIX}"
    
    if aws kinesis describe-stream --stream-name "$STREAM_NAME" 2>/dev/null; then
        echo "  ✓ Stream $STREAM_NAME exists"
    else
        # Start with 1 shard to minimize cost (can scale later)
        aws kinesis create-stream \
            --stream-name "$STREAM_NAME" \
            --shard-count 1
        
        echo "  ⏳ Creating $STREAM_NAME..."
        aws kinesis wait stream-exists --stream-name "$STREAM_NAME"
        
        # Add tags
        STREAM_ARN=$(aws kinesis describe-stream --stream-name "$STREAM_NAME" --query 'StreamDescription.StreamARN' --output text)
        aws kinesis add-tags-to-stream \
            --stream-arn "$STREAM_ARN" \
            --tags Environment=C_N,Component=$stream,Division=Oracle
        
        echo "  ✓ Created $STREAM_NAME (1 shard)"
    fi
done

echo "✅ Kinesis streams created (4 streams × 1 shard = ~$43/month)"