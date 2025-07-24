#!/bin/bash

# Quick Reference for Car Finder Updates
echo "🚀 Car Finder EC2 Update Quick Reference"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🎯 What did you change?${NC}"
echo ""

echo -e "${GREEN}🐍 Python backend only (src/ files):${NC}"
echo "   → ./quick-backend-fix.sh (3 min)"
echo ""

echo -e "${GREEN}🎨 Frontend only (frontend/ files):${NC}"
echo "   → ./rebuild-with-frontend.sh (5 min)"
echo ""

echo -e "${GREEN}🔧 Config only (.env, docker-compose.yml):${NC}"
echo "   → ./restart.sh (30 sec)"
echo ""

echo -e "${GREEN}💥 Both backend + frontend:${NC}"
echo "   → ./final-rebuild.sh (8 min)"
echo ""

echo -e "${YELLOW}🧹 Everything is broken:${NC}"
echo "   → ./cleanup-and-redeploy.sh (10 min)"
echo ""

echo "🔗 Full guide: cat UPDATE_WORKFLOW.md"
echo "📋 All scripts: ./scripts-guide.sh"
echo ""
echo "🌐 Your site: http://98.81.130.84:8001"
echo "🏥 Health: http://98.81.130.84:8001/health" 