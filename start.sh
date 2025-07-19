#!/bin/bash

# Car Finder Quick Start Script
# This script helps you get the Car Finder application running quickly

set -e  # Exit on any error

echo "🚀 Car Finder Quick Start"
echo "=========================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please create a .env file with the following content:"
    echo ""
    cat << 'EOF'
# Application Configuration
DEBUG=true
SECRET_KEY=your-super-secret-key-please-change-this
ALLOWED_HOSTS=*

# Database Configuration  
MONGODB_URL=mongodb://mongodb:27017/carfinder
MONGODB_DATABASE=carfinder
REDIS_URL=redis://redis:6379

# External API Keys (Not needed yet)
FIRECRAWL_API_KEY=not-needed-yet
PERPLEXITY_API_KEY=not-needed-yet

# SMTP Configuration (Optional)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TLS=true
EMAIL_FROM=noreply@carfinder.com

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=

# Business Configuration
MAX_SEARCHES_PER_USER=10
MAX_OPPORTUNITIES_PER_DAY=100
DEFAULT_SEARCH_INTERVAL_HOURS=2

# Regional Settings
TARGET_STATES=FL,GA
TRANSPORTATION_COST_PER_MILE=0.65
BASE_TRANSPORT_FEE=200.0

# API Rate Limits
FIRECRAWL_DAILY_LIMIT=1000
PERPLEXITY_DAILY_LIMIT=100
EOF
    echo ""
    echo "Save this as .env and run the script again."
    exit 1
fi

echo "✅ .env file found"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found!"
    echo "Please install docker-compose and try again."
    exit 1
fi

echo "✅ docker-compose is available"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down

# Build and start containers
echo "🏗️  Building and starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers are running"
else
    echo "❌ Some containers failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

# Test health endpoint
echo "🏥 Testing health endpoint..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API is not responding after 30 attempts"
        echo "Check logs with: docker-compose logs app"
        exit 1
    fi
    echo "⏳ Waiting for API... (attempt $i/30)"
    sleep 2
done

echo ""
echo "🎉 Car Finder is now running!"
echo ""
echo "📊 Access points:"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check:      http://localhost:8000/health"
echo "  • Alternative Docs:  http://localhost:8000/redoc"
echo ""
echo "🧪 Test the API:"
echo "  python3 test_api.py"
echo ""
echo "📋 Useful commands:"
echo "  • View logs:      docker-compose logs -f"
echo "  • Stop services:  docker-compose down"
echo "  • Restart:        docker-compose restart"
echo ""
echo "✨ Ready for development!" 