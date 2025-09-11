#!/bin/bash

# Deploy RDS PostgreSQL with pgvector for Continuum_Overworld
set -e

ENVIRONMENT=${1:-staging}
REGION=${AWS_REGION:-us-east-1}

echo "🗄️ Deploying RDS PostgreSQL for $ENVIRONMENT environment..."

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create parameter group for pgvector
aws rds create-db-parameter-group \
  --db-parameter-group-name "continuum-pg16-$ENVIRONMENT" \
  --db-parameter-group-family postgres16 \
  --description "PostgreSQL 16 with pgvector for Continuum_Overworld" \
  --region $REGION || echo "Parameter group already exists"

# Enable pgvector
aws rds modify-db-parameter-group \
  --db-parameter-group-name "continuum-pg16-$ENVIRONMENT" \
  --parameters "ParameterName=shared_preload_libraries,ParameterValue=vector,ApplyMethod=pending-reboot" \
  --region $REGION

# Create subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name "continuum-subnet-group-$ENVIRONMENT" \
  --db-subnet-group-description "Subnet group for Continuum_Overworld RDS" \
  --subnet-ids subnet-12345678 subnet-87654321 \
  --region $REGION || echo "Subnet group already exists"

# Create security group
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $REGION)
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name "continuum-rds-sg-$ENVIRONMENT" \
  --description "Security group for Continuum_Overworld RDS" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text 2>/dev/null || aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=continuum-rds-sg-$ENVIRONMENT" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Allow PostgreSQL access
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0 \
  --region $REGION || echo "Security group rule already exists"

# Determine instance class based on environment
if [ "$ENVIRONMENT" = "production" ]; then
  INSTANCE_CLASS="db.t3.medium"
  ALLOCATED_STORAGE=100
  BACKUP_RETENTION=7
  MULTI_AZ=true
else
  INSTANCE_CLASS="db.t3.micro"
  ALLOCATED_STORAGE=20
  BACKUP_RETENTION=1
  MULTI_AZ=false
fi

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier "continuum-$ENVIRONMENT" \
  --db-instance-class $INSTANCE_CLASS \
  --engine postgres \
  --engine-version 16.1 \
  --master-username bridge_admin \
  --master-user-password $DB_PASSWORD \
  --allocated-storage $ALLOCATED_STORAGE \
  --storage-type gp3 \
  --storage-encrypted \
  --vpc-security-group-ids $SECURITY_GROUP_ID \
  --db-parameter-group-name "continuum-pg16-$ENVIRONMENT" \
  --backup-retention-period $BACKUP_RETENTION \
  --multi-az $MULTI_AZ \
  --publicly-accessible \
  --auto-minor-version-upgrade \
  --region $REGION || echo "RDS instance already exists"

# Wait for instance to be available
echo "⏳ Waiting for RDS instance to be available..."
aws rds wait db-instance-available \
  --db-instance-identifier "continuum-$ENVIRONMENT" \
  --region $REGION

# Get endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "continuum-$ENVIRONMENT" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text \
  --region $REGION)

# Store credentials in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "continuum/$ENVIRONMENT/database" \
  --description "Database credentials for Continuum_Overworld $ENVIRONMENT" \
  --secret-string "{\"username\":\"bridge_admin\",\"password\":\"$DB_PASSWORD\",\"endpoint\":\"$DB_ENDPOINT\",\"port\":5432,\"dbname\":\"continuum\"}" \
  --region $REGION || echo "Secret already exists"

# Output connection string
PG_DSN="postgresql://bridge_admin:$DB_PASSWORD@$DB_ENDPOINT:5432/continuum"
echo "✅ RDS PostgreSQL deployed successfully!"
echo "📝 Connection string: $PG_DSN"
echo "🔐 Password stored in AWS Secrets Manager: continuum/$ENVIRONMENT/database"

# Set GitHub secret
if command -v gh &> /dev/null; then
  echo $PG_DSN | gh secret set PG_DSN_${ENVIRONMENT^^} -R $(git remote get-url origin)
  echo "🔑 GitHub secret PG_DSN_${ENVIRONMENT^^} updated"
fi