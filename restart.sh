#!/bin/bash

# Car Finder - Restart Script
echo "🔄 Restarting Car Finder services..."

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

# Stop services
print_info "Stopping services..."
docker-compose down

# Start services (without rebuilding)
print_info "Starting services..."
docker-compose up -d

# Wait for services
print_info "Waiting for services to start..."
sleep 30

# Check service health
print_info "Checking service health..."

# Check MongoDB
mongodb_healthy=false
for i in {1..3}; do
    if docker-compose exec -T car-finder-mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        print_success "MongoDB is running and healthy"
        mongodb_healthy=true
        break
    else
        print_warning "MongoDB check attempt $i/3 failed, waiting..."
        sleep 10
    fi
done

# Check Backend
backend_healthy=false
for i in {1..5}; do
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Car Finder Backend is running and healthy"
        backend_healthy=true
        break
    else
        print_warning "Backend health check attempt $i/5 failed, waiting..."
        sleep 10
    fi
done

# Show status
print_info "Service status:"
docker-compose ps

echo ""
if [ "$backend_healthy" = true ] && [ "$mongodb_healthy" = true ]; then
    print_success "Car Finder services restarted successfully! 🎉"
    echo ""
    echo "🌐 Car Finder App: http://localhost:8001"
    echo "📚 API Docs: http://localhost:8001/docs" 
    echo "📊 MongoDB Admin: http://localhost:8082"
else
    print_error "Some services failed to restart properly"
    print_info "Check logs: docker-compose logs -f"
    exit 1
fi

echo ""
print_info "View logs: docker-compose logs -f" 
print_info "Stop services: ./stop.sh" 