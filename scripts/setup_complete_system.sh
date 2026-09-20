#!/bin/bash
# Complete System Setup Script
# Run this after implementation to set up everything

set -e

echo "🚀 Loan Agent System - Complete Setup"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Docker services
echo -e "${YELLOW}Step 1: Checking Docker services...${NC}"
if ! docker-compose ps | grep -q "Up"; then
    echo "Starting Docker services..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
else
    echo -e "${GREEN}✓ Docker services already running${NC}"
fi

# Step 2: Install Python dependencies
echo -e "\n${YELLOW}Step 2: Installing Python dependencies...${NC}"
cd loan-agent-backend
if [ ! -d "venv" ]; then
    python3 -m venv ../venv
fi
source ../venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Run database migrations
echo -e "\n${YELLOW}Step 3: Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}✓ Database migrations complete${NC}"

# Step 4: Embed knowledge base
echo -e "\n${YELLOW}Step 4: Embedding knowledge base into ChromaDB...${NC}"
echo "This will take a few minutes..."
python scripts/embed_knowledge_base.py
echo -e "${GREEN}✓ Knowledge base embedded${NC}"

# Step 5: Check all services
echo -e "\n${YELLOW}Step 5: Verifying all services...${NC}"

# Check PostgreSQL
if docker exec loan-agent-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL: Running${NC}"
else
    echo -e "${RED}✗ PostgreSQL: Not responding${NC}"
fi

# Check Redis
if docker exec loan-agent-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis: Running${NC}"
else
    echo -e "${RED}✗ Redis: Not responding${NC}"
fi

# Check RabbitMQ
if curl -s http://localhost:15672 > /dev/null; then
    echo -e "${GREEN}✓ RabbitMQ: Running (http://localhost:15672)${NC}"
else
    echo -e "${RED}✗ RabbitMQ: Not responding${NC}"
fi

# Check ChromaDB
if curl -s http://localhost:8100/api/v1/heartbeat > /dev/null; then
    echo -e "${GREEN}✓ ChromaDB: Running (http://localhost:8100)${NC}"
else
    echo -e "${RED}✗ ChromaDB: Not responding${NC}"
fi

# Check Camunda
if curl -s http://localhost:8080/camunda > /dev/null; then
    echo -e "${GREEN}✓ Camunda: Running (http://localhost:8080)${NC}"
else
    echo -e "${RED}✗ Camunda: Not responding${NC}"
fi

# Check Camunda DMN
if curl -s http://localhost:8081/api/rules/health > /dev/null; then
    echo -e "${GREEN}✓ Camunda DMN: Running (http://localhost:8081)${NC}"
else
    echo -e "${RED}✗ Camunda DMN: Not responding${NC}"
fi

echo ""
echo -e "${GREEN}======================================"
echo "✅ Setup Complete!"
echo "======================================${NC}"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Start Backend API:"
echo "   cd loan-agent-backend"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "2. Start Background Worker (in new terminal):"
echo "   cd loan-agent-backend"
echo "   python workers/genai_worker.py"
echo ""
echo "3. Start Frontend (in new terminal):"
echo "   cd loan-agent-frontend"
echo "   npm run dev"
echo ""
echo "4. Access Application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000/docs"
echo "   RabbitMQ Management: http://localhost:15672 (admin/secret123)"
echo "   Camunda: http://localhost:8080/camunda (demo/demo)"
echo ""
echo "5. Test RAG Pipeline:"
echo "   python -c 'from app.services.genai.vector_store import get_vector_store; vs = get_vector_store(); print(vs.list_collections())'"
echo ""
echo -e "${YELLOW}⚠️  Important: Make sure to set your OPENAI_API_KEY in .env file${NC}"
echo ""
