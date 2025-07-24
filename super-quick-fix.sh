#!/bin/bash

# Super Quick Backend Fix: Static Files at Root
echo "🚀 Super Quick Fix: Serve ALL static files at root (favicons, icons, etc.)"

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

# Just restart the backend (no rebuild needed since we only changed Python code)
print_info "Restarting backend container with new static file configuration..."
docker-compose restart car-finder-backend

# Wait for backend to restart
print_info "Waiting 15 seconds for backend to restart..."
sleep 15

# Test backend health
print_info "Testing backend health..."
backend_healthy=false
for i in {1..3}; do
    print_info "Health check attempt $i/3..."
    if curl -f -s http://98.81.130.84:8001/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        backend_healthy=true
        break
    else
        print_warning "Backend not ready yet, waiting..."
        sleep 10
    fi
done

if [ "$backend_healthy" = false ]; then
    print_error "Backend failed to restart. Checking logs..."
    docker-compose logs --tail=15 car-finder-backend
    exit 1
fi

# Test the specific files that were failing
print_info "Testing problematic static files..."

echo ""
echo "Testing favicon and icon files:"

# Test car icon
print_info "Testing car-icon.svg..."
car_icon_response=$(curl -s -I http://98.81.130.84:8001/car-icon.svg)
if echo "$car_icon_response" | grep -q "200 OK"; then
    print_success "car-icon.svg is now accessible!"
else
    print_warning "car-icon.svg still has issues:"
    echo "$car_icon_response" | head -2
fi

# Test favicon
print_info "Testing favicon-32x32.png..."
favicon_response=$(curl -s -I http://98.81.130.84:8001/favicon-32x32.png)
if echo "$favicon_response" | grep -q "200 OK"; then
    print_success "favicon-32x32.png is accessible!"
else
    print_warning "favicon-32x32.png still has issues:"
    echo "$favicon_response" | head -2
fi

echo ""
echo "Testing core React assets:"

# Test main React JS
print_info "Testing main React JS..."
react_js_response=$(curl -s -I http://98.81.130.84:8001/assets/index-CAb82Wi1.js)
if echo "$react_js_response" | grep -q "200 OK"; then
    print_success "React JS is accessible!"
else
    print_warning "React JS has issues:"
    echo "$react_js_response" | head -2
fi

# Test React CSS
print_info "Testing React CSS..."
react_css_response=$(curl -s -I http://98.81.130.84:8001/assets/index-DycDOlqh.css)
if echo "$react_css_response" | grep -q "200 OK"; then
    print_success "React CSS is accessible!"
else
    print_warning "React CSS has issues:"
    echo "$react_css_response" | head -2
fi

# Test homepage
print_info "Testing homepage..."
homepage_response=$(curl -s http://98.81.130.84:8001/)
if echo "$homepage_response" | grep -q "Car Finder" || echo "$homepage_response" | grep -q "<!doctype html"; then
    print_success "Homepage HTML is being served!"
else
    print_warning "Homepage might not be served correctly."
fi

echo ""
echo "🎉 SUPER QUICK FIX COMPLETE!"
echo ""
echo "🌐 Try your Car Finder now: http://98.81.130.84:8001"
echo ""

# Check container status
print_info "Container status:"
docker-compose ps | grep car-finder-backend

echo ""
if [ "$backend_healthy" = true ]; then
    print_success "Static file configuration updated! React should now load with all assets! 🚀"
    print_info "If the page is still empty, try a hard refresh (Ctrl+F5 or Cmd+Shift+R)"
else
    print_error "Something went wrong. Check the logs above."
fi 