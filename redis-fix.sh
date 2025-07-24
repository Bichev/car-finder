#!/bin/bash

# Fix Redis connection issue and restart backend
echo "🔧 Fixing Redis connection issue and restarting backend..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Stop the problematic backend container
print_info "Stopping backend container..."
docker-compose stop car-finder-backend

# Remove the backend container and image to force rebuild
print_info "Removing backend container and image..."
docker rm car-finder-backend 2>/dev/null || true
docker rmi car-finder_car-finder-backend 2>/dev/null || true

# Rebuild and start just the backend (other services should keep running)
print_info "Rebuilding backend with Redis fix..."
docker-compose up --build -d car-finder-backend

# Wait for backend to start
print_info "Waiting for backend to start..."
sleep 20

# Check if backend is now running
if docker ps | grep -q "car-finder-backend.*Up"; then
    print_success "Backend container is now running!"
    
    # Test health endpoint
    print_info "Testing backend health..."
    sleep 5
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Backend is healthy and responding!"
        echo ""
        echo "🎉 Success! Car Finder is now running:"
        echo "🌐 Car Finder App: http://98.81.130.84:8001"
        echo "📊 MongoDB Admin:  http://98.81.130.84:8082"
        echo "📚 API Docs:       http://98.81.130.84:8001/docs"
        echo "🏥 Health Check:   http://98.81.130.84:8001/health"
    else
        print_warning "Backend started but health check failed. It may still be starting up..."
        echo "Wait a minute and try: curl http://localhost:8001/health"
    fi
else
    print_error "Backend container failed to start. Check logs:"
    echo "docker-compose logs car-finder-backend"
fi

# Show current status
echo ""
print_info "Current container status:"
docker-compose ps 