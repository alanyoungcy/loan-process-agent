# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Backend Fails to Start - NumPy Version Error

**Error:**
```
AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```

**Cause:** ChromaDB 0.4.22 is not compatible with NumPy 2.0+

**Solution:**
```bash
source venv/bin/activate
pip install "numpy<2.0"
```

**Fixed in:** `requirements.txt` now specifies `numpy==1.26.4`

---

### Issue 2: Port 8000 Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill all processes on port 8000
lsof -ti:8000 | xargs kill -9

# Restart backend
cd loan-agent-backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Issue 3: Frontend Can't Connect to Backend

**Symptoms:**
```
Failed to load resource: net::ERR_CONNECTION_TIMED_OUT
GET http://localhost:8000/api/v1/cases?limit=100
```

**Checks:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","database":"connected","redis":"connected"}`

2. Check backend logs:
   ```bash
   tail -f /tmp/backend.log
   ```

3. Restart backend if needed:
   ```bash
   pkill -f "uvicorn app.main:app"
   cd loan-agent-backend
   source ../venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### Issue 4: Docker Services Not Running

**Check Docker status:**
```bash
docker-compose ps
```

**Restart Docker services:**
```bash
docker-compose down
docker-compose up -d
```

**Wait for services to be ready:**
- PostgreSQL: ~10 seconds
- Redis: ~5 seconds
- RabbitMQ: ~15 seconds
- ChromaDB: ~10 seconds
- Camunda: ~30 seconds
- Drools: ~30 seconds

---

### Issue 5: Database Connection Error

**Error:**
```
Could not connect to database
```

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Test connection:
   ```bash
   docker exec loan-agent-postgres pg_isready -U admin
   ```

3. Check credentials in `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://admin:secret123@localhost:5432/loan_agent
   ```

---

### Issue 6: ChromaDB Connection Error

**Error:**
```
Failed to connect to ChromaDB
```

**Solution:**
1. Check ChromaDB is running:
   ```bash
   curl http://localhost:8100/api/v1/heartbeat
   ```

2. Restart ChromaDB:
   ```bash
   docker-compose restart chromadb
   ```

---

### Issue 7: RabbitMQ Not Accessible

**Check RabbitMQ:**
```bash
curl -u admin:secret123 http://localhost:15672/api/overview
```

**Restart if needed:**
```bash
docker-compose restart rabbitmq
```

---

### Issue 8: Frontend Build Fails

**Error:**
```
Module not found: bpmn-js
```

**Solution:**
```bash
cd loan-agent-frontend
npm install
```

**If still fails:**
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Quick Health Check Script

Save as `health_check.sh`:

```bash
#!/bin/bash

echo "Checking system health..."
echo ""

# Backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend: Running"
else
    echo "✗ Backend: Not responding"
fi

# Frontend
if curl -s http://localhost:5173 > /dev/null; then
    echo "✓ Frontend: Running"
else
    echo "✗ Frontend: Not responding"
fi

# PostgreSQL
if docker exec loan-agent-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "✓ PostgreSQL: Running"
else
    echo "✗ PostgreSQL: Not running"
fi

# Redis
if docker exec loan-agent-redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis: Running"
else
    echo "✗ Redis: Not running"
fi

# RabbitMQ
if curl -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✓ RabbitMQ: Running"
else
    echo "✗ RabbitMQ: Not running"
fi

# ChromaDB
if curl -s http://localhost:8100/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✓ ChromaDB: Running"
else
    echo "✗ ChromaDB: Not running"
fi

echo ""
echo "Health check complete!"
```

---

## Complete System Restart

If all else fails, do a complete restart:

```bash
# 1. Stop everything
pkill -f "uvicorn app.main:app"
pkill -f "npm run dev"
pkill -f "genai_worker.py"
docker-compose down

# 2. Wait a moment
sleep 5

# 3. Start Docker services
docker-compose up -d
sleep 15

# 4. Start backend
cd loan-agent-backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 5. Start worker
python workers/genai_worker.py &

# 6. Start frontend
cd ../loan-agent-frontend
npm run dev &

# 7. Wait and test
sleep 10
curl http://localhost:8000/health
```

---

## Environment Variables Check

Make sure your `.env` file in `loan-agent-backend` has:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://admin:secret123@localhost:5432/loan_agent

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://admin:secret123@localhost:5672/

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8100

# GenAI (set your actual keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security
SECRET_KEY=your-secret-key-change-in-production
```

---

## Log Locations

- **Backend:** `/tmp/backend.log` or console output
- **Worker:** `/tmp/worker.log` or console output
- **Frontend:** Console output
- **Docker:** `docker-compose logs -f [service_name]`

---

## Getting Help

1. Check this troubleshooting guide
2. Review relevant documentation in `DOCUMENTATION_INDEX.md`
3. Check logs for specific error messages
4. Verify all services are running: `./scripts/status.sh`

---

**Last Updated:** September 4, 2026  
**Issue Fixed:** NumPy 2.0 incompatibility with ChromaDB
