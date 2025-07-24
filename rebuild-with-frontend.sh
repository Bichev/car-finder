#!/bin/bash

# Rebuild backend with frontend included
echo "🔄 Rebuilding Car Finder with frontend included..."

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

# Step 1: Stop and clean up existing containers
print_info "Stopping all existing containers..."
docker-compose down

# Clean up any conflicting containers
print_info "Cleaning up conflicting containers..."
docker stop $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true

# Step 2: Remove old images to force rebuild
print_info "Removing old backend image..."
docker rmi car-finder_car-finder-backend 2>/dev/null || true
docker rmi car-finder-car-finder-backend:latest 2>/dev/null || true

# Step 3: Check if frontend is built locally
print_info "Checking frontend build..."
if [ ! -d "frontend/dist" ]; then
    print_error "Frontend not built! Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
    print_success "Frontend built successfully"
else
    print_success "Frontend already built"
fi

# Step 4: Clear Docker build cache to ensure fresh build
print_info "Clearing Docker build cache..."
docker builder prune -f

# Step 5: Build and start services with fresh images
print_info "Building and starting services..."
docker-compose up --build -d

# Step 6: Wait for services to start
print_info "Waiting for services to start..."
sleep 30

# Step 7: Check container status
print_info "Checking container status..."
docker-compose ps

# Step 8: Test backend health
print_info "Testing backend health..."
for i in {1..5}; do
    print_info "Health check attempt $i/5..."
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        
        # Test if frontend is served
        print_info "Testing frontend..."
        if curl -f -s http://localhost:8001/ | grep -q "Car Finder" 2>/dev/null; then
            print_success "Frontend is being served!"
        else
            print_warning "Backend healthy but frontend might not be built into container"
            print_info "Checking static files in container..."
            docker exec car-finder-backend ls -la /app/static/ || print_warning "Could not check static files"
        fi
        
        echo ""
        echo "🎉 SUCCESS! Car Finder should now be working:"
        echo "🌐 Car Finder App: http://98.81.130.84:8001"
        echo "📚 API Docs:       http://98.81.130.84:8001/docs"
        echo "🏥 Health Check:   http://98.81.130.84:8001/health"
        echo "📊 MongoDB Admin:  http://98.81.130.84:8082"
        break
    else
        print_warning "Health check failed, waiting 15 seconds..."
        sleep 15
    fi
    
    if [ $i -eq 5 ]; then
        print_error "Backend still not responding after 5 attempts"
        print_info "Checking logs:"
        docker-compose logs --tail=20 car-finder-backend
    fi
done

echo ""
print_info "Final container status:"
docker-compose ps 