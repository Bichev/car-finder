#!/bin/bash

# Final fix for extra environment variables
echo "🔧 Final fix: Making Settings model ignore extra environment variables..."

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

# Stop the backend container
print_info "Stopping backend container..."
docker-compose stop car-finder-backend

# Remove the backend container and image for fresh rebuild
print_info "Removing backend container and image..."
docker rm car-finder-backend 2>/dev/null || true
docker rmi car-finder_car-finder-backend 2>/dev/null || true

# Clear any build cache
print_info "Clearing Docker build cache..."
docker builder prune -f

# Rebuild and start the backend with the final fix
print_info "Rebuilding backend with Pydantic extra='ignore' fix..."
docker-compose up --build -d car-finder-backend

# Wait for backend to start
print_info "Waiting for backend to start..."
sleep 25

# Check container status
backend_status=$(docker ps --filter "name=car-finder-backend" --format "table {{.Status}}" | tail -n +2)
print_info "Backend container status: $backend_status"

if docker ps | grep -q "car-finder-backend.*Up"; then
    print_success "Backend container is running!"
    
    # Test health endpoint multiple times
    print_info "Testing backend health (may take a moment)..."
    
    for i in {1..5}; do
        print_info "Health check attempt $i/5..."
        if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "Backend is healthy and responding!"
            
            # Get actual response
            health_response=$(curl -s http://localhost:8001/health)
            print_success "Health response: $health_response"
            
            echo ""
            echo "🎉 SUCCESS! Car Finder is now fully operational:"
            echo "🌐 Car Finder App: http://98.81.130.84:8001"
            echo "📊 MongoDB Admin:  http://98.81.130.84:8082"  
            echo "📚 API Docs:       http://98.81.130.84:8001/docs"
            echo "🏥 Health Check:   http://98.81.130.84:8001/health"
            echo ""
            echo "🔧 The Pydantic validation issue is now resolved!"
            break
        else
            print_warning "Health check failed, waiting 10 seconds..."
            sleep 10
        fi
        
        if [ $i -eq 5 ]; then
            print_error "Health check still failing after 5 attempts"
            print_info "Checking backend logs for errors:"
            docker-compose logs --tail=20 car-finder-backend
        fi
    done
else
    print_error "Backend container failed to start or is not running"
    print_info "Container status:"
    docker-compose ps
    print_info "Backend logs:"
    docker-compose logs --tail=30 car-finder-backend
fi

echo ""
print_info "Final container status:"
docker-compose ps 