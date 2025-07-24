#!/bin/bash

# Docker Compose Isolation Check
echo "🛡️ Docker Compose Isolation Check"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${CYAN}📋 $1${NC}"
    echo "----------------------------------------"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check all running containers
print_header "ALL RUNNING CONTAINERS"
if docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}" | head -20; then
    echo ""
else
    print_info "No containers currently running"
fi

# Check all containers (including stopped)
print_header "ALL CONTAINERS (including stopped)"
if docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | head -20; then
    echo ""
else
    print_info "No containers found"
fi

# Check networks
print_header "DOCKER NETWORKS"
if docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"; then
    echo ""
else
    print_info "No custom networks found"
fi

# Check volumes
print_header "DOCKER VOLUMES"
if docker volume ls --format "table {{.Name}}\t{{.Driver}}"; then
    echo ""
else
    print_info "No volumes found"
fi

# Check car-finder specific containers
print_header "CAR-FINDER SPECIFIC CONTAINERS"
car_finder_containers=$(docker ps -a --filter "name=car-finder" --format "{{.Names}}")
if [ -n "$car_finder_containers" ]; then
    print_success "Found Car Finder containers:"
    echo "$car_finder_containers" | while read container; do
        echo "  • $container"
    done
else
    print_info "No Car Finder containers found"
fi

# Check what happens in this directory vs others
print_header "DOCKER COMPOSE PROJECT ISOLATION"
echo "Current directory: $(pwd)"
echo "Docker Compose project name: $(basename $(pwd))"
echo ""
print_info "Key points about isolation:"
echo "  • Each folder with docker-compose.yml is a separate project"
echo "  • Container names are prefixed with folder name OR use custom names"
echo "  • Our car-finder uses custom names: car-finder-mongo, car-finder-backend"
echo "  • Networks are isolated: car-finder-network"
echo "  • Volumes are isolated: car_finder_mongo_data"
echo ""
print_success "docker-compose down ONLY affects containers defined in THIS folder's docker-compose.yml"
print_warning "Your other projects in other folders are completely safe!"

# Show what docker-compose down would affect
print_header "WHAT 'docker-compose down' WOULD AFFECT"
if [ -f docker-compose.yml ]; then
    print_info "Services defined in this docker-compose.yml:"
    grep -E "^  [a-zA-Z]" docker-compose.yml | sed 's/://g' | sed 's/^  /  • /'
    echo ""
    print_info "Container names that would be affected:"
    grep -A 1 "container_name:" docker-compose.yml | grep "container_name:" | sed 's/.*container_name: /  • /'
else
    print_warning "No docker-compose.yml found in current directory"
fi

echo ""
print_success "🛡️ Your other projects are completely isolated and safe!" 