#!/bin/bash

echo "🚀 Starting Car Finder Development Environment with Hot Reload..."

# Load environment variables
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(cat .env | grep -v '#' | xargs)
else
    echo "⚠️  No .env file found. Make sure to set PERPLEXITY_API_KEY and FIRECRAWL_API_KEY"
fi

# Stop any running development containers
echo "🛑 Stopping any existing development containers..."
docker-compose -f docker-compose.dev.yml down

# Build and start development environment
echo "🔨 Building and starting development environment..."
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development environment started!"
echo ""
echo "🌐 Frontend (with hot reload): http://localhost:8001"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 MongoDB Admin: http://localhost:8082 (admin/admin123)"
echo ""
echo "📝 Now you can edit frontend/src/App.jsx and see changes instantly!"
echo "🔄 Any changes to your React components will automatically reload in the browser." 