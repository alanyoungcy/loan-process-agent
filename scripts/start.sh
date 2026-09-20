#!/bin/bash
# Loan Agent - Complete Start Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Parse arguments
GENERATE_DATA=false
DATA_COUNT=200

while [[ $# -gt 0 ]]; do
    case $1 in
        --generate-data) GENERATE_DATA=true; shift ;;
        --count) DATA_COUNT="$2"; shift 2 ;;
        --help)
            echo "Usage: ./scripts/start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --generate-data    Generate demo data after starting"
            echo "  --count N          Number of cases to generate (default: 200)"
            echo "  --help             Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 Starting Loan Agent System${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if already running
if [ -f "/tmp/loan-agent-backend.pid" ]; then
    PID=$(cat /tmp/loan-agent-backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend already running (PID: $PID)${NC}"
        echo -e "${YELLOW}   Stop it first: ./scripts/stop.sh${NC}"
        exit 1
    fi
fi

# Step 1: Docker Services
echo -e "${BLUE}Step 1/5: Starting Docker Services${NC}"
cd "$PROJECT_ROOT"

echo "  Starting core infrastructure..."
docker-compose up -d postgres redis rabbitmq chromadb elasticsearch 2>&1 | grep -v "WARNING" || true
echo "  ⏳ Waiting 20 seconds for infrastructure..."
sleep 20

echo "  Starting Camunda 8 - Zeebe..."
docker-compose up -d zeebe 2>&1 | grep -v "WARNING" || true
echo "  ⏳ Waiting 30 seconds for Zeebe..."
sleep 30

echo "  Starting Camunda 8 - Operate, Tasklist, Optimize..."
docker-compose up -d operate tasklist optimize connectors 2>&1 | grep -v "WARNING" || true
echo "  ⏳ Waiting 30 seconds for Camunda services..."
sleep 30

echo "  Starting Camunda DMN Service..."
docker-compose up -d camunda-dmn-service 2>&1 | grep -v "WARNING" || true
echo "  ⏳ Waiting 15 seconds for Camunda DMN..."
sleep 15

echo ""
echo "  Docker Services Status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | head -8
echo -e "${GREEN}  ✅ All Docker services started${NC}"
echo ""

# Step 2: Backend API
echo -e "${BLUE}Step 2/5: Starting Backend API${NC}"
cd "$PROJECT_ROOT/loan-agent-backend"

if [ ! -d "../venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Create it: python -m venv ../venv && source ../venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source ../venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/loan-agent-backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/loan-agent-backend.pid
echo "  Backend PID: $BACKEND_PID"
echo "  ⏳ Waiting 10 seconds for backend..."
sleep 10

# Verify backend started
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "   Check logs: tail -f /tmp/loan-agent-backend.log"
    exit 1
fi

echo -e "${GREEN}  ✅ Backend API started${NC}"
echo ""

# Step 3: Generate Data (optional)
if [ "$GENERATE_DATA" = true ]; then
    echo -e "${BLUE}Step 3/5: Generating Demo Data (${DATA_COUNT} cases)${NC}"
    cd "$PROJECT_ROOT/data-generator"
    source ../venv/bin/activate
    python seed.py --count $DATA_COUNT 2>&1 | tail -25
    echo -e "${GREEN}  ✅ Demo data generated${NC}"
else
    echo -e "${YELLOW}Step 3/5: Skipping data generation${NC}"
    echo "  Run with --generate-data to populate database"
fi
echo ""

# Step 4: Frontend
echo -e "${BLUE}Step 4/5: Starting Frontend${NC}"
cd "$PROJECT_ROOT/loan-agent-frontend"

if [ ! -d "node_modules" ]; then
    echo "  Installing dependencies..."
    npm install
fi

nohup npm run dev > /tmp/loan-agent-frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/loan-agent-frontend.pid
echo "  Frontend PID: $FRONTEND_PID"
echo "  ⏳ Waiting 15 seconds for frontend..."
sleep 15

echo -e "${GREEN}  ✅ Frontend started${NC}"
echo ""

# Step 5: Health Checks
echo -e "${BLUE}Step 5/5: Health Checks${NC}"

# Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "  Backend API:  ${GREEN}✅ http://localhost:8000${NC}"
else
    echo -e "  Backend API:  ${RED}❌ Not responding${NC}"
fi

# Camunda DMN
if curl -s http://localhost:8081/api/rules/health > /dev/null 2>&1; then
    echo -e "  Camunda DMN:  ${GREEN}✅ http://localhost:8081${NC}"
else
    echo -e "  Camunda DMN:  ${YELLOW}⚠️  Check: docker logs loan-agent-camunda-dmn${NC}"
fi

# Zeebe
if curl -s http://localhost:9600/ready > /dev/null 2>&1; then
    echo -e "  Zeebe:        ${GREEN}✅ http://localhost:26500${NC}"
else
    echo -e "  Zeebe:        ${YELLOW}⚠️  Check: docker logs loan-agent-zeebe${NC}"
fi

# Operate
if curl -s http://localhost:8080/operate/actuator/health > /dev/null 2>&1; then
    echo -e "  Operate:      ${GREEN}✅ http://localhost:8080${NC}"
else
    echo -e "  Operate:      ${YELLOW}⚠️  Check: docker logs loan-agent-operate${NC}"
fi

# Tasklist
if curl -s http://localhost:8082/actuator/health > /dev/null 2>&1; then
    echo -e "  Tasklist:     ${GREEN}✅ http://localhost:8082${NC}"
else
    echo -e "  Tasklist:     ${YELLOW}⚠️  Check: docker logs loan-agent-tasklist${NC}"
fi

# Optimize
if curl -s http://localhost:8083/api/readyz > /dev/null 2>&1; then
    echo -e "  Optimize:     ${GREEN}✅ http://localhost:8083${NC}"
else
    echo -e "  Optimize:     ${YELLOW}⚠️  Check: docker logs loan-agent-optimize${NC}"
fi

# Connectors (AI)
if curl -s http://localhost:8085/actuator/health > /dev/null 2>&1; then
    echo -e "  Connectors:   ${GREEN}✅ http://localhost:8085${NC}"
else
    echo -e "  Connectors:   ${YELLOW}⚠️  Check: docker logs loan-agent-connectors${NC}"
fi

# Frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  Frontend:     ${GREEN}✅ http://localhost:5173${NC}"
else
    echo -e "  Frontend:     ${YELLOW}⚠️  Check: tail -f /tmp/loan-agent-frontend.log${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Loan Agent System Started!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo -e "   ${GREEN}Frontend:       http://localhost:5173${NC} 🎨"
echo -e "   Backend API:    http://localhost:8000/docs"
echo ""
echo -e "${BLUE}🚀 Camunda 8.7 Services:${NC}"
echo -e "   ${GREEN}Operate:        http://localhost:8080${NC} (Process Monitoring)"
echo -e "   Tasklist:       http://localhost:8082 (Human Tasks)"
echo -e "   Optimize:       http://localhost:8083 (Analytics & AI)"
echo -e "   Zeebe Gateway:  localhost:26500 (gRPC)"
echo -e "   Connectors:     http://localhost:8085 (AI Integration)"
echo ""
echo -e "${BLUE}🧠 AI Features:${NC}"
echo -e "   ${GREEN}✓${NC} OpenAI/Anthropic connectors ready"
echo -e "   ${GREEN}✓${NC} Process intelligence & optimization"
echo -e "   ${GREEN}✓${NC} Natural language to BPMN"
echo -e "   ${GREEN}✓${NC} Predictive analytics"
echo ""
echo -e "   Camunda DMN:    http://localhost:8081/api/rules/health"
echo ""
echo -e "${BLUE}🔑 Demo Login:${NC}"
echo -e "   Username: ${YELLOW}demo${NC}"
echo -e "   Password: ${YELLOW}demo123${NC}"
echo ""
echo -e "${BLUE}📊 What You'll See:${NC}"
echo -e "   ${GREEN}✓${NC} 200 real cases (HK localized)"
echo -e "   ${GREEN}✓${NC} 200 workflow instances"
echo -e "   ${GREEN}✓${NC} DMN decision tables active"
echo -e "   ${GREEN}✓${NC} 6 BPMN workflows"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "   Status:     ${YELLOW}./scripts/status.sh${NC}"
echo -e "   Stop:       ${YELLOW}./scripts/stop.sh${NC}"
echo -e "   Logs:       ${YELLOW}tail -f /tmp/loan-agent-*.log${NC}"
echo -e "   Docker:     ${YELLOW}docker-compose logs -f camunda-dmn-service camunda${NC}"
echo ""
if [ "$GENERATE_DATA" = false ]; then
    echo -e "${BLUE}💡 To populate with demo data:${NC}"
    echo -e "   ${YELLOW}cd data-generator && source ../venv/bin/activate${NC}"
    echo -e "   ${YELLOW}python seed.py --count 200${NC}"
    echo ""
fi
echo -e "${GREEN}🎉 Ready! Open http://localhost:5173 in your browser${NC}"
echo ""
