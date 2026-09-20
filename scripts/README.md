# Loan Agent Scripts

This directory contains convenience scripts for managing the Loan Agent system.

## Available Scripts

### 🚀 start.sh
**Start all Loan Agent services**

```bash
./scripts/start.sh
```

**What it does**:
1. Starts Docker services (PostgreSQL, Redis, RabbitMQ, ChromaDB)
2. Activates Python virtual environment
3. Starts FastAPI backend on port 8000
4. Starts React frontend on port 5173
5. Performs health checks

**Access**: http://localhost:5173

---

### 🛑 stop.sh
**Stop all Loan Agent services**

```bash
./scripts/stop.sh
```

Gracefully stops all services and cleans up processes.

---

### 📊 status.sh
**Check status of all services**

```bash
./scripts/status.sh
```

Shows status of backend, frontend, and Docker services.

---

### 🔄 restart.sh
**Restart all services**

```bash
./scripts/restart.sh
```

Stops and starts all services with a 3-second pause.

---

## Quick Start

```bash
# First time
chmod +x scripts/*.sh
./scripts/start.sh

# Check status
./scripts/status.sh

# Access app
open http://localhost:5173
```

## Service URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Workflows**: http://localhost:5173/workflows
- **Rules**: http://localhost:5173/rules

## Default Credentials

- Admin: `admin` / `admin123`
- Collector: `collector1` / `collector123`
- Demo: `demo` / `demo123`

## Logs

```bash
tail -f /tmp/loan-agent-backend.log
tail -f /tmp/loan-agent-frontend.log
```

## Troubleshooting

```bash
# Full restart
./scripts/stop.sh && ./scripts/start.sh

# Check what's running
./scripts/status.sh

# Kill port 5173
lsof -ti:5173 | xargs kill -9

# Kill port 8000
lsof -ti:8000 | xargs kill -9
```
