#!/bin/bash
# Loan Agent - Complete Stop Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🛑 Stopping Loan Agent System${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Stop Backend
echo -e "${BLUE}Step 1/3: Stopping Backend API${NC}"
if [ -f "/tmp/loan-agent-backend.pid" ]; then
    BACKEND_PID=$(cat /tmp/loan-agent-backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "  Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        rm /tmp/loan-agent-backend.pid
        echo -e "${GREEN}  ✅ Backend stopped${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Backend not running${NC}"
        rm /tmp/loan-agent-backend.pid
    fi
else
    # Try to find and kill any uvicorn process
    pkill -f "uvicorn app.main:app" 2>/dev/null && echo -e "${GREEN}  ✅ Backend stopped${NC}" || echo -e "${YELLOW}  ⚠️  Backend not running${NC}"
fi
echo ""

# Stop Frontend
echo -e "${BLUE}Step 2/3: Stopping Frontend${NC}"
if [ -f "/tmp/loan-agent-frontend.pid" ]; then
    FRONTEND_PID=$(cat /tmp/loan-agent-frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "  Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        rm /tmp/loan-agent-frontend.pid
        echo -e "${GREEN}  ✅ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Frontend not running${NC}"
        rm /tmp/loan-agent-frontend.pid
    fi
else
    # Try to find and kill any vite/npm process
    pkill -f "npm run dev" 2>/dev/null && echo -e "${GREEN}  ✅ Frontend stopped${NC}" || echo -e "${YELLOW}  ⚠️  Frontend not running${NC}"
fi
echo ""

# Stop Docker Services
echo -e "${BLUE}Step 3/3: Stopping Docker Services${NC}"
cd "$PROJECT_ROOT"

if command -v docker-compose &> /dev/null; then
    echo "  Stopping all Docker containers..."
    docker-compose down 2>&1 | grep -v "WARNING" || true
    echo -e "${GREEN}  ✅ Docker services stopped${NC}"
else
    echo -e "${RED}  ❌ docker-compose not found${NC}"
fi
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Loan Agent System Stopped${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📝 To start again:${NC}"
echo -e "   ${YELLOW}./scripts/start.sh${NC}"
echo ""
echo -e "${BLUE}🗑️  To clean up volumes (removes all data):${NC}"
echo -e "   ${YELLOW}docker-compose down -v${NC}"
echo ""
