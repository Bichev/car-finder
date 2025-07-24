#!/bin/bash

# Car Finder - Scripts Guide
echo "🎯 Car Finder Scripts Guide"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_title() {
    echo -e "${CYAN}📜 $1${NC}"
}

print_usage() {
    echo -e "${GREEN}   Usage: $1${NC}"
}

print_description() {
    echo -e "${BLUE}   $1${NC}"
}

print_note() {
    echo -e "${YELLOW}   💡 $1${NC}"
}

echo ""
print_title "DEPLOYMENT SCRIPTS"
echo "----------------------------------------"

echo ""
print_title "1. deploy.sh"
print_usage "./deploy.sh"
print_description "🚀 Complete deployment with frontend build and health checks"
print_description "   • Builds frontend if needed"
print_description "   • Stops existing containers"
print_description "   • Builds and starts all services"
print_description "   • Runs comprehensive health checks"
print_note "Use for: First deployment or when you want full rebuild"

echo ""
print_title "2. restart.sh"
print_usage "./restart.sh"
print_description "🔄 Quick restart without rebuilding"
print_description "   • Stops and starts existing containers"
print_description "   • No rebuild, uses existing images"
print_description "   • Includes health checks"
print_note "Use for: Quick restart when no code changes"

echo ""
print_title "3. stop.sh"
print_usage "./stop.sh"
print_description "🛑 Stop all services cleanly"
print_description "   • Stops all containers"
print_description "   • Preserves data in volumes"
print_note "Use for: Stopping services when done"

echo ""
print_title "REBUILD SCRIPTS"
echo "----------------------------------------"

echo ""
print_title "4. rebuild-with-frontend.sh"
print_usage "./rebuild-with-frontend.sh"
print_description "🎨 Complete rebuild with frontend focus"
print_description "   • Ensures frontend is built"
print_description "   • Forces fresh Docker build"
print_description "   • Tests both backend and frontend"
print_note "Use for: When frontend changes or homepage is empty"

echo ""
print_title "5. quick-backend-fix.sh"
print_usage "./quick-backend-fix.sh"
print_description "⚡ Fast fix for FastAPI static file serving"
print_description "   • Fixes React assets not loading (empty frontend)"
print_description "   • Rebuilds only backend (2-3 minutes)"
print_description "   • Tests static file serving"
print_description "   • No Playwright reinstall needed"
print_note "Use for: When frontend shows empty page but containers are running"

echo ""
print_title "6. final-rebuild.sh"
print_usage "./final-rebuild.sh"
print_description "🔧 Ultimate fix for Playwright + Frontend issues"
print_description "   • Fixes Playwright browser installation (as appuser)"
print_description "   • Ensures frontend is properly built and served"
print_description "   • Complete clean slate rebuild"
print_description "   • Extended wait times for Playwright download"
print_description "   • Comprehensive testing of all components"
print_note "Use for: When both Playwright and frontend are broken"

echo ""
print_title "7. cleanup-and-redeploy.sh"
print_usage "./cleanup-and-redeploy.sh"
print_description "🧹 Nuclear cleanup and fresh start"
print_description "   • Removes ALL car-finder containers and images"
print_description "   • Cleans Docker cache completely"
print_description "   • Rebuilds frontend from scratch"
print_description "   • Calls deploy.sh for fresh start"
print_note "Use for: When everything is broken and you need a clean slate"

echo ""
print_title "TROUBLESHOOTING SCRIPTS"
echo "----------------------------------------"

echo ""
print_title "8. final-fix.sh"
print_usage "./final-fix.sh"
print_description "🔧 Fix Pydantic validation errors"
print_description "   • Rebuilds with Settings extra='ignore'"
print_description "   • Multiple health check attempts"
print_note "Use for: When getting Pydantic validation errors"

echo ""
print_title "9. redis-fix.sh"
print_usage "./redis-fix.sh"
print_description "⚡ Fix Redis connection issues"
print_description "   • Makes Redis connection optional"
print_note "Use for: When getting Redis connection errors"

echo ""
print_title "UTILITY SCRIPTS"
echo "----------------------------------------"

echo ""
print_title "10. check-isolation.sh"
print_usage "./check-isolation.sh"
print_description "🔍 Verify Docker isolation"
print_description "   • Shows all containers and networks"
print_description "   • Explains project isolation"
print_note "Use for: Verifying that your project is isolated from others"

echo ""
print_title "11. test-deployment.sh"
print_usage "./test-deployment.sh"
print_description "🧪 Test deployment health"
print_description "   • Tests all endpoints"
print_description "   • Verifies database connections"
print_note "Use for: Verifying deployment is working correctly"

echo ""
echo "========================================"
echo -e "${GREEN}✅ QUICK REFERENCE:${NC}"
echo "• First time: ./deploy.sh"
echo "• Quick restart: ./restart.sh"  
echo "• Empty frontend: ./quick-backend-fix.sh"
echo "• Frontend issues: ./rebuild-with-frontend.sh"
echo "• Playwright + Frontend issues: ./final-rebuild.sh"
echo "• Everything broken: ./cleanup-and-redeploy.sh"
echo "• Just stop: ./stop.sh"
echo ""
echo -e "${BLUE}📊 Check status: docker-compose ps${NC}"
echo -e "${BLUE}📝 View logs: docker-compose logs -f${NC}"
echo "" 