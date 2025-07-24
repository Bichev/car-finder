#!/bin/bash

# Car Finder - Cleanup and Redeploy Script
echo "🧹 Cleaning up failed build and redeploying..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Stop any running containers
print_info "Stopping any running containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Stop and remove any car-finder related containers
print_info "Cleaning up all car-finder containers..."
docker stop $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true

# Remove car-finder specific images
print_info "Removing car-finder images..."
docker rmi $(docker images | grep car-finder | awk '{print $3}') 2>/dev/null || true

# Remove dangling images and unused resources
print_info "Cleaning up Docker system..."
docker system prune -f

# Clear build cache completely
print_info "Clearing Docker build cache..."
docker builder prune -af

# Clean up frontend if needed
print_info "Checking frontend..."
if [ -d "frontend/node_modules" ]; then
    print_warning "Removing frontend node_modules for clean install..."
    rm -rf frontend/node_modules
fi

if [ -d "frontend/dist" ]; then
    print_warning "Removing frontend build for fresh build..."
    rm -rf frontend/dist
fi

# Show disk space
print_info "Docker disk usage after cleanup:"
docker system df

print_success "Cleanup complete!"

# Verify environment
print_info "Verifying environment..."
if [ ! -f .env ]; then
    print_warning ".env file not found, copying from example..."
    cp env.example .env
    print_warning "Please edit .env file with your API keys!"
fi

# Now redeploy with comprehensive build
print_info "Starting fresh deployment with full rebuild..."
./deploy.sh 