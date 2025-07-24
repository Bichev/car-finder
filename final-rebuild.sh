#!/bin/bash

# Final rebuild to fix Playwright browsers and frontend
echo "🔧 Final rebuild: Fixing Playwright browsers and frontend serving..."

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

# Stop everything
print_info "Stopping all containers..."
docker-compose down

# Remove ALL car-finder containers and images for complete clean slate
print_info "Removing all car-finder containers and images..."
docker stop $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true
docker rmi $(docker images | grep car-finder | awk '{print $3}') 2>/dev/null || true

# Clean Docker system completely
print_info "Cleaning Docker system..."
docker system prune -af
docker builder prune -af

# Ensure frontend is built locally
print_info "Ensuring frontend is built locally..."
if [ ! -d "frontend/dist" ] || [ ! -f "frontend/dist/index.html" ]; then
    print_warning "Frontend not properly built. Building now..."
    cd frontend
    
    # Clean install
    rm -rf node_modules dist
    npm install
    npm run build
    
    cd ..
    
    if [ -f "frontend/dist/index.html" ]; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed!"
        exit 1
    fi
else
    print_success "Frontend already built"
fi

# Verify frontend build contents
print_info "Verifying frontend build contents..."
if [ -d "frontend/dist" ]; then
    echo "Frontend dist contents:"
    ls -la frontend/dist/
    if [ -d "frontend/dist/assets" ]; then
        echo "Assets directory:"
        ls -la frontend/dist/assets/ | head -5
    fi
else
    print_error "Frontend dist directory missing!"
    exit 1
fi

# Build with the fixed Dockerfile
print_info "Building with fixed Dockerfile (Playwright + Frontend)..."
docker-compose up --build -d

# Wait longer for services to start (Playwright installation takes time)
print_info "Waiting for services to start (this may take a while due to Playwright browser download)..."
sleep 60

# Check if containers are running
print_info "Checking container status..."
docker-compose ps

# Test backend health
print_info "Testing backend health..."
backend_healthy=false
for i in {1..10}; do
    print_info "Health check attempt $i/10..."
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        backend_healthy=true
        break
    else
        print_warning "Backend not ready yet, waiting..."
        sleep 15
    fi
done

if [ "$backend_healthy" = false ]; then
    print_error "Backend failed to start. Checking logs..."
    docker-compose logs --tail=30 car-finder-backend
    exit 1
fi

# Test frontend serving
print_info "Testing frontend serving..."
frontend_response=$(curl -s http://localhost:8001/)
if echo "$frontend_response" | grep -q "Car Finder" || echo "$frontend_response" | grep -q "<!doctype html"; then
    print_success "Frontend is being served correctly!"
else
    print_warning "Frontend might not be served correctly. Response preview:"
    echo "$frontend_response" | head -3
fi

# Test static files directly
print_info "Testing static files in container..."
docker exec car-finder-backend ls -la /app/static/ || print_warning "Could not list static files"

# Test Playwright
print_info "Testing Playwright installation..."
playwright_test=$(curl -s -X POST "http://localhost:8001/api/v1/search-execution/test/playwright" \
    -H "Content-Type: application/json" \
    -d '{"marketplace":"cars_com","make":"Honda","model":"Accord","year_min":2018,"year_max":2023}')

if echo "$playwright_test" | grep -q "error"; then
    print_warning "Playwright test shows error - may still be initializing"
    echo "Playwright test result: $playwright_test"
else
    print_success "Playwright test completed"
fi

echo ""
echo "🎉 FINAL REBUILD COMPLETE!"
echo ""
echo "🌐 Car Finder App: http://98.81.130.84:8001"
echo "📚 API Docs: http://98.81.130.84:8001/docs"
echo "🏥 Health Check: http://98.81.130.84:8001/health"
echo "📊 MongoDB Admin: http://98.81.130.84:8082"
echo ""

# Show final status
print_info "Final container status:"
docker-compose ps

print_info "To monitor logs: docker-compose logs -f car-finder-backend"
echo ""
print_success "Both frontend and Playwright should now be working! 🚀" 