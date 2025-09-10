#!/bin/bash

echo "🐳 Helios Console - Docker Setup"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or not accessible from WSL"
    echo ""
    echo "Please ensure:"
    echo "1. Docker Desktop is running on Windows"
    echo "2. WSL integration is enabled in Docker Desktop settings"
    echo "   - Open Docker Desktop"
    echo "   - Go to Settings > Resources > WSL Integration"
    echo "   - Enable integration with your WSL distro"
    echo ""
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    if ! docker compose version &> /dev/null; then
        echo "❌ docker-compose not found"
        exit 1
    else
        COMPOSE_CMD="docker compose"
    fi
else
    COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker Compose is available"
echo ""

# Choose mode
echo "Select mode:"
echo "1) Development (with hot reload) - Port 3000"
echo "2) Production build - Port 3001"
echo ""
read -p "Choose [1-2]: " choice

case $choice in
    1)
        echo "🚀 Starting development server..."
        echo ""
        echo "Building and starting Helios Console in development mode..."
        echo "This may take a few minutes on first run..."
        echo ""
        
        $COMPOSE_CMD up --build helios-console-dev
        ;;
    2)
        echo "🏗️ Starting production build..."
        echo ""
        echo "Building and starting Helios Console in production mode..."
        echo "This may take a few minutes on first run..."
        echo ""
        
        $COMPOSE_CMD --profile production up --build helios-console-prod
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac