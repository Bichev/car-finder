#!/bin/bash

# Fix Pydantic validation error and restart
echo "🔧 Fixing Pydantic validation error and restarting..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Stop current containers
print_info "Stopping containers..."
docker-compose down

# Remove the problematic backend container
print_info "Removing failed backend container and image..."
docker rm car-finder-backend 2>/dev/null || true
docker rmi car-finder_car-finder-backend 2>/dev/null || true

# Start again with fixed configuration
print_info "Starting with fixed configuration..."
docker-compose up --build -d

# Wait for services
print_info "Waiting for services to start..."
sleep 30

# Check status
print_info "Checking service status..."
docker-compose ps

# Test backend health
print_info "Testing backend health..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Backend is now working!"
    echo ""
    echo "🎉 Success! Services are running:"
    echo "🌐 Car Finder App: http://localhost:8001"
    echo "📊 MongoDB Admin:  http://localhost:8082"
    echo "📚 API Docs:       http://localhost:8001/docs"
else
    print_error "Backend still not responding. Check logs:"
    echo "docker-compose logs car-finder-backend"
fi 