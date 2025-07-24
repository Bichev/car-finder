#!/bin/bash

# Car Finder - Deployment Test Script
echo "🧪 Testing Car Finder deployment..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Test 1: Check if containers are running
print_info "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    print_success "Containers are running"
else
    print_error "Containers are not running"
    exit 1
fi

# Test 2: Check health endpoint
print_info "Testing health endpoint..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Health endpoint responding"
else
    print_error "Health endpoint not responding"
fi

# Test 3: Check MongoDB connection
print_info "Testing MongoDB connection..."
if docker-compose exec -T car-finder-mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    print_success "MongoDB connection working"
else
    print_error "MongoDB connection failed"
fi

# Test 4: Test API endpoint
print_info "Testing API endpoint..."
if curl -f http://localhost:8001/docs > /dev/null 2>&1; then
    print_success "API documentation accessible"
else
    print_warning "API documentation not accessible"
fi

# Test 5: Test car search endpoint
print_info "Testing car search functionality..."
response=$(curl -s -X POST http://localhost:8001/api/v1/search-execution/test/playwright \
  -H "Content-Type: application/json" \
  -d '{
    "marketplace": "cars_com",
    "make": "Honda",
    "model": "Accord",
    "year_min": 2020,
    "year_max": 2023,
    "price_min": 20000,
    "price_max": 35000,
    "location_zip": "33101",
    "headless": true,
    "timeout_seconds": 30
  }')

if echo "$response" | grep -q "success"; then
    print_success "Car search API working"
else
    print_warning "Car search API may need configuration"
fi

echo ""
echo "🎯 Test Summary:"
echo "----------------------------------------"
docker-compose ps

echo ""
print_info "If all tests passed, your Car Finder is ready!"
print_info "Access at: http://localhost:8001" 