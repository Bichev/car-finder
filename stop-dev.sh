#!/bin/bash

echo "🛑 Stopping Car Finder Development Environment..."

# Stop development containers
docker-compose -f docker-compose.dev.yml down

echo "✅ Development environment stopped!"
echo ""
echo "💡 To start development mode again: ./start-dev.sh"
echo "🚀 To start production mode: ./start.sh" 