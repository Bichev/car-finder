#!/bin/bash

echo "🚀 Building Car Finder for production..."

# Build frontend
echo "📦 Building React frontend..."
cd frontend
npm ci
npm run build
cd ..

# Create static directory
echo "📁 Setting up static files..."
mkdir -p static
cp -r frontend/dist/* static/

echo "✅ Build complete!"
echo "📋 To test locally:"
echo "   python -m src.main"
echo "   Then visit: http://localhost:8000" 