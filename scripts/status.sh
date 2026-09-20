#!/bin/bash

# Loan Agent - Status Script
# This script shows the status of all services

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="/tmp/loan-agent-backend.pid"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📊 Loan Agent System Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Backend API
echo -e "${BLUE}🔧 Backend API:${NC}"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "   Status: ${GREEN}✅ Running${NC} (PID: $PID)"

        # Check if responding
        HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
        if echo "$HEALTH" | grep -q "healthy"; then
            echo -e "   Health: ${GREEN}✅ Healthy${NC}"
            echo -e "   URL:    ${GREEN}http://localhost:8000${NC}"
            echo -e "   Docs:   ${GREEN}http://localhost:8000/docs${NC}"
        else
            echo -e "   Health: ${YELLOW}⚠️  Not responding${NC}"
        fi
    else
        echo -e "   Status: ${RED}❌ Not running${NC} (stale PID file)"
        rm "$PID_FILE"
    fi
else
    echo -e "   Status: ${RED}❌ Not running${NC}"
fi

echo ""

# Check Docker Services
echo -e "${BLUE}📦 Docker Services:${NC}"
cd "$PROJECT_ROOT"

# PostgreSQL
POSTGRES_STATUS=$(docker inspect --format='{{.State.Status}}' loan-agent-postgres 2>/dev/null || echo "not found")
POSTGRES_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' loan-agent-postgres 2>/dev/null || echo "unknown")
if [ "$POSTGRES_STATUS" = "running" ]; then
    if [ "$POSTGRES_HEALTH" = "healthy" ]; then
        echo -e "   PostgreSQL: ${GREEN}✅ Running & Healthy${NC} (localhost:5432)"
    else
        echo -e "   PostgreSQL: ${YELLOW}⚠️  Running but $POSTGRES_HEALTH${NC}"
    fi
else
    echo -e "   PostgreSQL: ${RED}❌ $POSTGRES_STATUS${NC}"
fi

# Redis
REDIS_STATUS=$(docker inspect --format='{{.State.Status}}' loan-agent-redis 2>/dev/null || echo "not found")
REDIS_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' loan-agent-redis 2>/dev/null || echo "unknown")
if [ "$REDIS_STATUS" = "running" ]; then
    if [ "$REDIS_HEALTH" = "healthy" ]; then
        echo -e "   Redis:      ${GREEN}✅ Running & Healthy${NC} (localhost:6379)"
    else
        echo -e "   Redis:      ${YELLOW}⚠️  Running but $REDIS_HEALTH${NC}"
    fi
else
    echo -e "   Redis:      ${RED}❌ $REDIS_STATUS${NC}"
fi

# RabbitMQ
RABBITMQ_STATUS=$(docker inspect --format='{{.State.Status}}' loan-agent-rabbitmq 2>/dev/null || echo "not found")
RABBITMQ_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' loan-agent-rabbitmq 2>/dev/null || echo "unknown")
if [ "$RABBITMQ_STATUS" = "running" ]; then
    if [ "$RABBITMQ_HEALTH" = "healthy" ]; then
        echo -e "   RabbitMQ:   ${GREEN}✅ Running & Healthy${NC} (localhost:5672, mgmt:15672)"
    else
        echo -e "   RabbitMQ:   ${YELLOW}⚠️  Running but $RABBITMQ_HEALTH${NC}"
    fi
else
    echo -e "   RabbitMQ:   ${RED}❌ $RABBITMQ_STATUS${NC}"
fi

# ChromaDB
CHROMA_STATUS=$(docker inspect --format='{{.State.Status}}' loan-agent-chromadb 2>/dev/null || echo "not found")
if [ "$CHROMA_STATUS" = "running" ]; then
    echo -e "   ChromaDB:   ${GREEN}✅ Running${NC} (localhost:8100)"
else
    echo -e "   ChromaDB:   ${RED}❌ $CHROMA_STATUS${NC}"
fi

echo ""

# Check GenAI Configuration
echo -e "${BLUE}🤖 GenAI Configuration:${NC}"
if [ -f "$PROJECT_ROOT/loan-agent-backend/.env" ]; then
    OPENAI_KEY=$(grep "^OPENAI_API_KEY=" "$PROJECT_ROOT/loan-agent-backend/.env" | cut -d'=' -f2)
    OPENAI_URL=$(grep "^OPENAI_BASE_URL=" "$PROJECT_ROOT/loan-agent-backend/.env" | cut -d'=' -f2)
    OPENAI_MODEL=$(grep "^OPENAI_MODEL=" "$PROJECT_ROOT/loan-agent-backend/.env" | cut -d'=' -f2)
    LLM_PROVIDER=$(grep "^DEFAULT_LLM_PROVIDER=" "$PROJECT_ROOT/loan-agent-backend/.env" | cut -d'=' -f2)

    if [ -n "$OPENAI_KEY" ] && [ "$OPENAI_KEY" != "sk-your-openai-key-here" ]; then
        echo -e "   Provider:   ${GREEN}✅ $LLM_PROVIDER${NC}"
        echo -e "   Base URL:   ${GREEN}$OPENAI_URL${NC}"
        echo -e "   Model:      ${GREEN}$OPENAI_MODEL${NC}"
        echo -e "   API Key:    ${GREEN}✅ Configured${NC} (${OPENAI_KEY:0:15}...)"
    else
        echo -e "   Provider:   ${YELLOW}⚠️  Not configured${NC}"
    fi
else
    echo -e "   ${RED}❌ .env file not found${NC}"
fi

echo ""

# System Resources
echo -e "${BLUE}💾 System Resources:${NC}"
if command -v docker &> /dev/null; then
    CONTAINER_COUNT=$(docker ps -q | wc -l | xargs)
    echo -e "   Running Containers: ${GREEN}$CONTAINER_COUNT${NC}"

    # Show container resource usage
    echo -e "   Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep "loan-agent" | while read line; do
        echo -e "      $line"
    done
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📝 Quick Commands:${NC}"
echo -e "   Start:   ${YELLOW}./scripts/start.sh${NC}"
echo -e "   Stop:    ${YELLOW}./scripts/stop.sh${NC}"
echo -e "   Restart: ${YELLOW}./scripts/restart.sh${NC}"
echo -e "   Logs:    ${YELLOW}tail -f /tmp/loan-agent-backend.log${NC}"
echo ""
