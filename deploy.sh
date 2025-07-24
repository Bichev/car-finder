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
    print_info "  - EC2_PUBLIC_IP"
    print_info "  - Update passwords"
    read -p "Press Enter after updating .env file to continue..."
fi

# Stop existing containers if running
print_info "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Remove old images (optional - comment out to speed up deployments)
print_info "Cleaning up old images..."
docker system prune -f || true

# Build and start services
print_info "Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
print_info "Waiting for services to start..."
sleep 30

# Check service health
print_info "Checking service health..."

# Check MongoDB
if docker-compose exec -T car-finder-mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    print_success "MongoDB is running"
else
    print_error "MongoDB failed to start"
fi

# Check Backend
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Car Finder Backend is running"
else
    print_error "Car Finder Backend failed to start"
fi

# Display service URLs
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Service URLs:"
echo "----------------------------------------"
echo "🌐 Car Finder App:      http://localhost:8001"
if [ -f .env ] && grep -q "EC2_PUBLIC_IP" .env; then
    EC2_IP=$(grep "EC2_PUBLIC_IP" .env | cut -d'=' -f2)
    if [ "$EC2_IP" != "your.ec2.public.ip" ]; then
        echo "🌐 Car Finder (Public): http://$EC2_IP:8001"
    fi
fi
echo "📊 MongoDB Admin:       http://localhost:8082"
echo "📚 API Documentation:   http://localhost:8001/docs"
echo "🏥 Health Check:        http://localhost:8001/health"
echo ""

# Show logs
echo "📝 Recent logs:"
echo "----------------------------------------"
docker-compose logs --tail=20 car-finder-backend

echo ""
print_info "To view logs: docker-compose logs -f"
print_info "To stop: ./stop.sh"
print_info "To restart: ./restart.sh"

echo ""
print_success "Car Finder is now running in isolated Docker containers! 🐳" 