#!/bin/bash
# The_Bridge Infrastructure Startup Script

set -e

echo "🌉 Starting The_Bridge Data Foundation..."
echo "========================================="

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env from sample..."
    cp .env.sample .env
    echo "   ⚠️  Please review .env and update passwords!"
fi

# Start infrastructure
echo "🚀 Starting Docker services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
until docker exec bridge_postgres pg_isready -U bridge_admin -d continuum; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "   ✅ PostgreSQL is ready"

# Check Redpanda
echo "🔍 Checking Redpanda..."
until docker exec bridge_redpanda rpk cluster health | grep -q "Healthy"; do
    echo "   Waiting for Redpanda..."
    sleep 2
done
echo "   ✅ Redpanda is ready"

# Check MinIO
echo "🔍 Checking MinIO..."
until curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    echo "   Waiting for MinIO..."
    sleep 2
done
echo "   ✅ MinIO is ready"

# Initialize database schemas
echo "📊 Initializing database schemas..."
for sql_file in ../The_Bridge/Console--Database__PROD@/schema/*.sql; do
    echo "   Loading $(basename $sql_file)..."
    docker exec -i bridge_postgres psql -U bridge_admin -d continuum < "$sql_file"
done
echo "   ✅ Database schemas created"

# Create MinIO buckets
echo "📦 Creating MinIO buckets..."
docker exec bridge_minio mc alias set local http://localhost:9000 bridge_admin bridge_secure_2025
docker exec bridge_minio mc mb -p local/lake-bronze || true
docker exec bridge_minio mc mb -p local/lake-silver || true
docker exec bridge_minio mc mb -p local/lake-gold || true
docker exec bridge_minio mc mb -p local/memory-artifacts || true
echo "   ✅ MinIO buckets created"

# Create Kafka topics
echo "📨 Creating Kafka topics..."
docker exec bridge_redpanda rpk topic create continuum.events -p 3 -r 1 || true
docker exec bridge_redpanda rpk topic create continuum.memory -p 3 -r 1 || true
docker exec bridge_redpanda rpk topic create continuum.metrics -p 3 -r 1 || true
echo "   ✅ Kafka topics created"

# Run verification
echo ""
echo "🔍 Running verification tests..."
python3 verify_bridge.py

echo ""
echo "========================================="
echo "🎉 The_Bridge is operational!"
echo ""
echo "📊 Services:"
echo "   PostgreSQL:     localhost:5432"
echo "   Redpanda:       localhost:19092"
echo "   Schema Registry: localhost:18081"
echo "   MinIO Console:  http://localhost:9001"
echo "   Neo4j Browser:  http://localhost:7474"
echo "   DataHub:        http://localhost:9002"
echo ""
echo "🔑 Default Credentials:"
echo "   PostgreSQL: bridge_admin / bridge_secure_2025"
echo "   MinIO:      bridge_admin / bridge_secure_2025"
echo "   Neo4j:      neo4j / bridge_secure_2025"
echo ""
echo "⚠️  Remember to update passwords in production!"
echo "========================================="