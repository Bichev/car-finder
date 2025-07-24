#!/bin/bash

# Quick backend fix for FastAPI static file serving
echo "🔧 Quick Backend Fix: FastAPI Static File Serving"

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

# Stop and remove just the backend container
print_info "Stopping backend container..."
docker-compose stop car-finder-backend
docker-compose rm -f car-finder-backend

# Remove just the backend image to force rebuild
print_info "Removing backend image..."
docker rmi $(docker images | grep car-finder-backend | awk '{print $3}') 2>/dev/null || true

# Rebuild and start just the backend
print_info "Rebuilding backend with FastAPI fix..."
docker-compose up --build -d car-finder-backend

# Wait for backend to start
print_info "Waiting for backend to start..."
sleep 15

# Test backend health
print_info "Testing backend health..."
backend_healthy=false
for i in {1..5}; do
    print_info "Health check attempt $i/5..."
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        backend_healthy=true
        break
    else
        print_warning "Backend not ready yet, waiting..."
        sleep 10
    fi
done

if [ "$backend_healthy" = false ]; then
    print_error "Backend failed to start. Checking logs..."
    docker-compose logs --tail=20 car-finder-backend
    exit 1
fi

# Test static file serving
print_info "Testing static file serving..."

# Test assets directory
assets_response=$(curl -s -I http://98.81.130.84:8001/assets/)
if echo "$assets_response" | grep -q "200 OK"; then
    print_success "Assets are being served correctly!"
else
    print_warning "Assets might not be served correctly. Response:"
    echo "$assets_response" | head -3
fi

# Test frontend page
print_info "Testing frontend page..."
frontend_response=$(curl -s http://98.81.130.84:8001/)
if echo "$frontend_response" | grep -q "Car Finder" || echo "$frontend_response" | grep -q "<!doctype html"; then
    print_success "Frontend HTML is being served!"
else
    print_warning "Frontend might not be served correctly."
fi

# Test specific asset file (if it exists)
print_info "Testing specific asset files..."
docker exec car-finder-backend ls -la /app/static/assets/ | head -5

echo ""
echo "🎉 BACKEND FIX COMPLETE!"
echo ""
echo "🌐 Try your Car Finder now: http://98.81.130.84:8001"
echo "📚 API Docs: http://98.81.130.84:8001/docs"
echo ""

print_info "Container status:"
docker-compose ps | grep car-finder-backend

echo ""
if [ "$backend_healthy" = true ]; then
    print_success "FastAPI static file fix deployed! React should now load properly! 🚀"
else
    print_error "Something went wrong. Check the logs above."
fi 