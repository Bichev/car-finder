#!/bin/bash

# Car Finder - Restart Script
echo "🔄 Restarting Car Finder services..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Stop services
print_info "Stopping services..."
docker-compose down

# Start services (without rebuilding)
print_info "Starting services..."
docker-compose up -d

# Wait for services
print_info "Waiting for services to start..."
sleep 15

# Show status
print_info "Service status:"
docker-compose ps

print_success "Car Finder services restarted"
print_info "View logs: docker-compose logs -f" 