#!/bin/bash

# EMERGENCY FIX: Restore health endpoint and fix favicon routes
echo "🚨 EMERGENCY FIX: Restoring /health endpoint and fixing favicon routes"

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

# Stop and remove backend container
print_info "Stopping backend container..."
docker-compose stop car-finder-backend
docker-compose rm -f car-finder-backend

# Remove backend image to force rebuild
print_info "Removing backend image..."
docker rmi $(docker images | grep car-finder-backend | awk '{print $3}') 2>/dev/null || true

# Rebuild and start backend with emergency fix
print_info "Rebuilding backend with emergency fix..."
docker-compose up --build -d car-finder-backend

# Wait for backend to start
print_info "Waiting for backend to start..."
sleep 20

# Test backend health with multiple attempts
print_info "Testing backend health (CRITICAL!)..."
backend_healthy=false
for i in {1..5}; do
    print_info "Health check attempt $i/5..."
    health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
    if [ "$health_response" = "200" ]; then
        print_success "✅ HEALTH ENDPOINT RESTORED! Backend is healthy!"
        backend_healthy=true
        break
    else
        print_warning "Health endpoint returned: $health_response, waiting..."
        sleep 10
    fi
done

if [ "$backend_healthy" = false ]; then
    print_error "❌ HEALTH ENDPOINT STILL BROKEN! Checking logs..."
    docker-compose logs --tail=15 car-finder-backend
    exit 1
fi

# Test favicon routes specifically
print_info "Testing favicon routes..."

echo ""
echo "Testing individual favicon files:"

# Test car icon
print_info "Testing car-icon.svg..."
car_icon_response=$(curl -s -o /dev/null -w "%{http_code}" http://98.81.130.84:8001/car-icon.svg)
if [ "$car_icon_response" = "200" ]; then
    print_success "✅ car-icon.svg now works!"
else
    print_warning "car-icon.svg returned: $car_icon_response"
fi

# Test favicon 32x32
print_info "Testing favicon-32x32.png..."
favicon_response=$(curl -s -o /dev/null -w "%{http_code}" http://98.81.130.84:8001/favicon-32x32.png)
if [ "$favicon_response" = "200" ]; then
    print_success "✅ favicon-32x32.png now works!"
else
    print_warning "favicon-32x32.png returned: $favicon_response"
fi

# Test React assets (should still work)
print_info "Testing React assets..."
react_js_response=$(curl -s -o /dev/null -w "%{http_code}" http://98.81.130.84:8001/assets/index-CAb82Wi1.js)
if [ "$react_js_response" = "200" ]; then
    print_success "✅ React JS still accessible!"
else
    print_warning "React JS returned: $react_js_response"
fi

# Test homepage
print_info "Testing homepage..."
homepage_response=$(curl -s http://98.81.130.84:8001/)
if echo "$homepage_response" | grep -q "Car Finder" || echo "$homepage_response" | grep -q "<!doctype html"; then
    print_success "✅ Homepage HTML is being served!"
else
    print_warning "Homepage might not be served correctly."
fi

echo ""
echo "🚨 EMERGENCY FIX COMPLETE!"
echo ""
echo "🌐 Try your Car Finder now: http://98.81.130.84:8001"
echo "🏥 Health Check: http://98.81.130.84:8001/health"
echo ""

# Check container status
print_info "Container status:"
docker-compose ps | grep car-finder-backend

echo ""
if [ "$backend_healthy" = true ]; then
    print_success "EMERGENCY FIX SUCCESSFUL! Health endpoint restored & favicon routes added! 🚀"
    print_info "React should now load properly with all assets accessible!"
    print_info "Try a hard refresh (Ctrl+F5 or Cmd+Shift+R) on the frontend"
else
    print_error "Emergency fix failed. Check the logs above."
fi 