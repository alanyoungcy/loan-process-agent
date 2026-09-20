# 🚀 Quick Start Guide

## Start Everything

```bash
cd /Volumes/Orico/code/capco/loan-agent
./scripts/start.sh
```

**If database is empty, add --generate-data:**
```bash
./scripts/start.sh --generate-data
```

## Access

- **Frontend**: http://localhost:5173
- **Login**: demo / demo123

## Management Commands

```bash
# Check status
./scripts/status.sh

# Stop system
./scripts/stop.sh

# Restart
./scripts/stop.sh && ./scripts/start.sh

# View logs
tail -f /tmp/loan-agent-backend.log
tail -f /tmp/loan-agent-frontend.log
docker-compose logs -f drools-service camunda
```

## What You Get

- ✅ 200 HK-localized cases
- ✅ 40+ Drools rules active
- ✅ 6 BPMN workflows
- ✅ Full dashboard with statistics

## Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 8000 | http://localhost:8000/docs |
| Drools | 8081 | http://localhost:8081/api/rules/health |
| Camunda | 8080 | http://localhost:8080/camunda |

## Troubleshooting

**Backend not starting?**
```bash
tail -f /tmp/loan-agent-backend.log
```

**Frontend not loading?**
```bash
tail -f /tmp/loan-agent-frontend.log
```

**Docker issues?**
```bash
docker-compose ps
docker-compose logs drools-service
docker-compose logs camunda
```

**Database empty?**
```bash
cd data-generator
source ../venv/bin/activate
python seed.py --reset --count 200
```

---

**Status**: ✅ All systems operational and ready!
