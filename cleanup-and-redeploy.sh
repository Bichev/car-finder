#!/bin/bash

# Car Finder - Cleanup and Redeploy Script
echo "🧹 Cleaning up failed build and redeploying..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# Stop any running containers
print_info "Stopping any running containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Remove failed build containers and images
print_info "Cleaning up failed builds..."
docker system prune -f

# Remove specific images if they exist
print_info "Removing car-finder images..."
docker rmi $(docker images | grep car-finder | awk '{print $3}') 2>/dev/null || true

# Clear build cache
print_info "Clearing Docker build cache..."
docker builder prune -f

# Show disk space
print_info "Docker disk usage:"
docker system df

print_success "Cleanup complete!"

# Now redeploy
print_info "Starting fresh deployment..."
./deploy.sh 