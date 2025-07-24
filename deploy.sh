#!/bin/bash

# Car Finder - EC2 Deployment Script
set -e

echo "🚀 Starting Car Finder deployment on EC2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    cp env.example .env
    print_info "Please edit .env file with your configuration:"
    print_info "  - PERPLEXITY_API_KEY"
    print_info "  - FIRECRAWL_API_KEY (optional)"
    print_info "  - Update passwords"
    read -p "Press Enter after updating .env file to continue..."
fi

# Check if frontend is built, build if necessary
print_info "Checking frontend build..."
if [ ! -d "frontend/dist" ]; then
    print_warning "Frontend not built. Building now..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies..."
        npm install
    fi
    print_info "Building frontend..."
    npm run build
    cd ..
    print_success "Frontend built successfully"
else
    print_success "Frontend already built"
fi

# Stop existing containers if running
print_info "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Clean up any conflicting containers
print_info "Cleaning up conflicting containers..."
docker stop $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=car-finder") 2>/dev/null || true

# Remove old images to force fresh build
print_info "Removing old backend image for fresh build..."
docker rmi car-finder_car-finder-backend 2>/dev/null || true

# Clear build cache for clean build
print_info "Clearing Docker build cache..."
docker builder prune -f

# Build and start services
print_info "Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
print_info "Waiting for services to start..."
sleep 30

# Check service health with multiple attempts
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

if [ "$mongodb_healthy" = false ]; then
    print_error "MongoDB failed to start properly"
fi

# Check Backend with multiple attempts
backend_healthy=false
for i in {1..5}; do
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Car Finder Backend is running and healthy"
        
        # Check if frontend is being served
        if curl -f -s http://localhost:8001/ | grep -q "Car Finder" 2>/dev/null; then
            print_success "Frontend is being served correctly"
        else
            print_warning "Backend healthy but frontend might not be properly served"
        fi
        
        backend_healthy=true
        break
    else
        print_warning "Backend health check attempt $i/5 failed, waiting..."
        sleep 15
    fi
done

if [ "$backend_healthy" = false ]; then
    print_error "Car Finder Backend failed to start properly"
    print_info "Checking backend logs:"
    docker-compose logs --tail=20 car-finder-backend
fi

# Display service URLs
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Service URLs:"
echo "----------------------------------------"
echo "🌐 Car Finder App:      http://localhost:8001"
echo "📊 MongoDB Admin:       http://localhost:8082"
echo "📚 API Documentation:   http://localhost:8001/docs"
echo "🏥 Health Check:        http://localhost:8001/health"
echo ""

# Show container status
print_info "Container status:"
docker-compose ps

echo ""
print_info "To view logs: docker-compose logs -f"
print_info "To stop: ./stop.sh"
print_info "To restart: ./restart.sh"
print_info "To rebuild with frontend: ./rebuild-with-frontend.sh"

echo ""
if [ "$backend_healthy" = true ] && [ "$mongodb_healthy" = true ]; then
    print_success "Car Finder is now running successfully in isolated Docker containers! 🐳"
else
    print_error "Some services failed to start properly. Check logs for details."
    exit 1
fi 