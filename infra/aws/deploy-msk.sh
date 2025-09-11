#!/bin/bash

# Deploy Amazon MSK (Kafka) for Continuum_Overworld event streaming
set -e

ENVIRONMENT=${1:-staging}
REGION=${AWS_REGION:-us-east-1}

echo "📨 Deploying Amazon MSK for $ENVIRONMENT environment..."

# Get VPC and subnets
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $REGION)
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0:2].SubnetId' --output text --region $REGION)
SUBNET1=$(echo $SUBNETS | cut -d' ' -f1)
SUBNET2=$(echo $SUBNETS | cut -d' ' -f2)

# Create security group for MSK
MSK_SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name "continuum-msk-sg-$ENVIRONMENT" \
  --description "Security group for Continuum_Overworld MSK" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text 2>/dev/null || aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=continuum-msk-sg-$ENVIRONMENT" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Allow Kafka ports
for PORT in 9092 9094 9098 2181; do
  aws ec2 authorize-security-group-ingress \
    --group-id $MSK_SECURITY_GROUP_ID \
    --protocol tcp \
    --port $PORT \
    --cidr 10.0.0.0/16 \
    --region $REGION || echo "Port $PORT rule already exists"
done

# Determine cluster configuration based on environment
if [ "$ENVIRONMENT" = "production" ]; then
  INSTANCE_TYPE="kafka.m5.large"
  STORAGE_SIZE=100
  NUM_BROKER_NODES=3
else
  INSTANCE_TYPE="kafka.t3.small"
  STORAGE_SIZE=20
  NUM_BROKER_NODES=2
fi

# Create MSK cluster configuration
CLUSTER_CONFIG_ARN=$(aws kafka create-configuration \
  --name "continuum-$ENVIRONMENT-config" \
  --description "MSK configuration for Continuum_Overworld $ENVIRONMENT" \
  --kafka-versions "2.8.1" \
  --server-properties "
auto.create.topics.enable=true
default.replication.factor=2
min.insync.replicas=1
num.partitions=3
log.retention.hours=168
log.segment.bytes=1073741824
" \
  --region $REGION \
  --query 'Arn' \
  --output text 2>/dev/null || aws kafka list-configurations \
  --query "Configurations[?Name=='continuum-$ENVIRONMENT-config'].Arn" \
  --output text \
  --region $REGION)

# Create cluster
cat > /tmp/msk-cluster.json << EOF
{
  "BrokerNodeGroupInfo": {
    "InstanceType": "$INSTANCE_TYPE",
    "ClientSubnets": ["$SUBNET1", "$SUBNET2"],
    "SecurityGroups": ["$MSK_SECURITY_GROUP_ID"],
    "StorageInfo": {
      "EBSStorageInfo": {
        "VolumeSize": $STORAGE_SIZE
      }
    }
  },
  "ClusterName": "continuum-$ENVIRONMENT",
  "KafkaVersion": "2.8.1",
  "NumberOfBrokerNodes": $NUM_BROKER_NODES,
  "EncryptionInfo": {
    "EncryptionInTransit": {
      "ClientBroker": "TLS",
      "InCluster": true
    }
  },
  "ClientAuthentication": {
    "Sasl": {
      "Scram": {
        "Enabled": false
      }
    },
    "Tls": {
      "Enabled": false
    }
  },
  "ConfigurationInfo": {
    "Arn": "$CLUSTER_CONFIG_ARN",
    "Revision": 1
  }
}
EOF

CLUSTER_ARN=$(aws kafka create-cluster \
  --cli-input-json file:///tmp/msk-cluster.json \
  --region $REGION \
  --query 'ClusterArn' \
  --output text 2>/dev/null || aws kafka list-clusters \
  --query "ClusterInfoList[?ClusterName=='continuum-$ENVIRONMENT'].ClusterArn" \
  --output text \
  --region $REGION)

echo "⏳ Waiting for MSK cluster to be active..."
aws kafka wait cluster-active \
  --cluster-arn $CLUSTER_ARN \
  --region $REGION

# Get bootstrap servers
BOOTSTRAP_SERVERS=$(aws kafka get-bootstrap-brokers \
  --cluster-arn $CLUSTER_ARN \
  --region $REGION \
  --query 'BootstrapBrokerString' \
  --output text)

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "continuum/$ENVIRONMENT/kafka" \
  --description "Kafka configuration for Continuum_Overworld $ENVIRONMENT" \
  --secret-string "{\"bootstrap_servers\":\"$BOOTSTRAP_SERVERS\",\"cluster_arn\":\"$CLUSTER_ARN\"}" \
  --region $REGION || echo "Secret already exists"

echo "✅ Amazon MSK deployed successfully!"
echo "📝 Bootstrap servers: $BOOTSTRAP_SERVERS"
echo "🔐 Configuration stored in AWS Secrets Manager: continuum/$ENVIRONMENT/kafka"

# Set GitHub secret
if command -v gh &> /dev/null; then
  echo $BOOTSTRAP_SERVERS | gh secret set KAFKA_BOOTSTRAP_SERVERS_${ENVIRONMENT^^} -R $(git remote get-url origin)
  echo "🔑 GitHub secret KAFKA_BOOTSTRAP_SERVERS_${ENVIRONMENT^^} updated"
fi

# Clean up temp file
rm -f /tmp/msk-cluster.json