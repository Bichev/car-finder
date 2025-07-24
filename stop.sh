#!/bin/bash

# Car Finder - Stop Script
echo "🛑 Stopping Car Finder services..."

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

# Stop all services
docker-compose down

print_success "Car Finder services stopped"
print_info "Data is preserved in Docker volumes"
print_info "To start again: ./deploy.sh or ./restart.sh" 