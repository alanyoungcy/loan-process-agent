# Camunda 8.7 Upgrade Guide

## Overview

Successfully upgraded from **Camunda Platform 7.20** to **Camunda Platform 8.7** with full AI capabilities.

## What Changed

### Architecture Transformation

#### Old Architecture (Camunda 7)
```
Single monolithic container:
- Camunda BPM Platform 7.20
- REST API on port 8080
- Embedded H2/PostgreSQL database
```

#### New Architecture (Camunda 8.7)
```
Microservices-based:
- Zeebe (Workflow Engine) - Port 26500 (gRPC), 9600 (monitoring)
- Operate (Process Monitoring) - Port 8080
- Tasklist (User Tasks) - Port 8082
- Optimize (Analytics & AI) - Port 8083
- Connectors (AI/External Systems) - Port 8085
- Elasticsearch (Data Store) - Port 9200
```

## New Services & Ports

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| **Zeebe** | 26500 | gRPC Gateway for workflow engine | - |
| **Operate** | 8080 | Process monitoring & management | http://localhost:8080 |
| **Tasklist** | 8082 | Human task management | http://localhost:8082 |
| **Optimize** | 8083 | Analytics & AI features | http://localhost:8083 |
| **Connectors** | 8085 | AI connectors (OpenAI, etc.) | http://localhost:8085 |
| **Elasticsearch** | 9200 | Search & data storage | http://localhost:9200 |
| **DMN Service** | 8081 | DMN rules engine | http://localhost:8081 |

## AI Capabilities Added

### 1. **OpenAI/Anthropic Integration**
- Direct integration via Connectors service
- Use GPT-4, Claude in workflows
- Sentiment analysis, text generation, classification

### 2. **Process Intelligence**
- AI-powered process mining
- Predictive analytics
- Bottleneck detection
- Optimization recommendations

### 3. **Smart Task Routing**
- ML-based task assignment
- Skill matching
- Workload balancing

### 4. **Natural Language to BPMN**
- Describe workflows in plain English
- Auto-generate BPMN diagrams
- AI-assisted modeling

## Breaking Changes

### 1. API Changes

**Old (Camunda 7):**
```bash
# Deploy process
POST http://localhost:8080/engine-rest/deployment/create

# Start instance
POST http://localhost:8080/engine-rest/process-definition/key/{key}/start
```

**New (Camunda 8):**
```bash
# Deploy process (via Zeebe client - gRPC)
# Use Zeebe client libraries or Operate UI

# Start instance (via Zeebe)
# Use Zeebe client or Operate API
```

### 2. BPMN Namespace Changes

**Old:**
```xml
<bpmn:definitions xmlns:camunda="http://camunda.org/schema/1.0/bpmn">
```

**New:**
```xml
<bpmn:definitions xmlns:zeebe="http://camunda.org/schema/zeebe/1.0">
```

### 3. Service Task Configuration

**Old (Camunda 7):**
```xml
<bpmn:serviceTask id="task" camunda:delegateExpression="${myDelegate}">
```

**New (Camunda 8):**
```xml
<bpmn:serviceTask id="task">
  <bpmn:extensionElements>
    <zeebe:taskDefinition type="myJobType" />
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

## Migration Steps

### 1. Update Environment Variables

Add to `.env`:
```bash
# Camunda 8 Configuration
ZEEBE_GATEWAY_ADDRESS=localhost:26500
CAMUNDA_OPERATE_URL=http://localhost:8080
CAMUNDA_TASKLIST_URL=http://localhost:8082
CAMUNDA_OPTIMIZE_URL=http://localhost:8083
CAMUNDA_CONNECTORS_URL=http://localhost:8085

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. Convert Existing BPMN Files

Use the Camunda 7 to 8 migration tool:

```bash
# Install migration tool
npm install -g @camunda/migration-tool

# Convert BPMN files
camunda-migrate --input ./camunda-deployments/*.bpmn --output ./camunda-8-deployments/
```

Or manually update:
- Change namespace from `camunda` to `zeebe`
- Update service task definitions
- Convert external tasks to job workers

### 3. Update Backend Code

**Old:**
```python
from app.services.camunda.client import get_camunda_client

camunda_client = get_camunda_client()
await camunda_client.start_process("myProcess", variables)
```

**New:**
```python
from app.services.camunda.zeebe_client import zeebe_client

await zeebe_client.start_process_instance("myProcess", variables)
```

### 4. Start Services

```bash
# Pull new images
docker-compose pull

# Start all services
docker-compose up -d

# Wait for services to be healthy (~2-3 minutes)
docker-compose ps

# Check logs
docker-compose logs -f zeebe operate
```

### 5. Verify Installation

```bash
# Check Zeebe
curl http://localhost:9600/ready

# Check Operate
curl http://localhost:8080/operate/actuator/health

# Check Connectors
curl http://localhost:8085/actuator/health

# Check Elasticsearch
curl http://localhost:9200/_cluster/health
```

## Updated Scripts

All scripts have been updated:
- `scripts/start.sh` - Now starts Camunda 8 services
- `scripts/stop.sh` - Stops all Camunda 8 containers
- `scripts/status.sh` - Checks Camunda 8 health

## Data Migration

### Existing Process Instances

⚠️ **Important**: Camunda 7 and 8 use different data models. Running instances in Camunda 7 cannot be directly migrated.

**Options:**
1. **Complete existing instances** in Camunda 7 before switching
2. **Run parallel** - Keep Camunda 7 for old instances, use Camunda 8 for new
3. **Manual migration** - Export/transform/import (complex)

### Historical Data

Use Camunda 7 History API to export completed instances, then import into Optimize for analytics.

## Resource Requirements

### Minimum Resources

| Component | CPU | Memory |
|-----------|-----|--------|
| Zeebe | 1 core | 512MB |
| Operate | 0.5 core | 512MB |
| Tasklist | 0.5 core | 512MB |
| Optimize | 1 core | 1GB |
| Connectors | 0.5 core | 512MB |
| Elasticsearch | 1 core | 2GB |
| **Total** | **4.5 cores** | **4.5GB** |

### Recommended Resources

| Component | CPU | Memory |
|-----------|-----|--------|
| Zeebe | 2 cores | 1GB |
| Operate | 1 core | 1GB |
| Tasklist | 1 core | 1GB |
| Optimize | 2 cores | 2GB |
| Connectors | 1 core | 1GB |
| Elasticsearch | 2 cores | 4GB |
| **Total** | **9 cores** | **11GB** |

## Performance Tuning

### Zeebe Performance

```yaml
# In docker-compose.yml
zeebe:
  environment:
    - ZEEBE_BROKER_EXECUTION_METRICS_EXPORTER_ENABLED=true
    - ZEEBE_BROKER_BACKPRESSURE_ENABLED=true
    - ZEEBE_BROKER_THREADS_CPUTHREADCOUNT=2
    - JAVA_OPTS=-Xms512m -Xmx2g
```

### Elasticsearch Performance

```yaml
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    - indices.query.bool.max_clause_count=4096
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs zeebe
docker-compose logs elasticsearch

# Increase memory
# Edit docker-compose.yml and increase ES_JAVA_OPTS

# Check disk space
df -h
```

### Connectors Not Working

```bash
# Verify API keys
docker exec loan-agent-connectors env | grep API_KEY

# Check connectivity to Zeebe
docker exec loan-agent-connectors curl zeebe:26500

# Restart connectors
docker-compose restart connectors
```

### Slow Performance

1. **Increase Elasticsearch heap**: ES_JAVA_OPTS=-Xms4g -Xmx4g
2. **Add more Zeebe partitions**: ZEEBE_BROKER_CLUSTER_PARTITIONSCOUNT=3
3. **Scale horizontally**: Run multiple Zeebe brokers

## Rollback Plan

If you need to rollback to Camunda 7:

```bash
# 1. Stop Camunda 8
docker-compose down

# 2. Restore old docker-compose.yml from backup
cp docker-compose.yml.backup docker-compose.yml

# 3. Start Camunda 7
docker-compose up -d camunda

# 4. Update backend config
# Revert CAMUNDA_URL to http://localhost:8080/engine-rest
```

## Benefits Realized

✅ **AI-Powered Workflows** - Direct OpenAI/Anthropic integration
✅ **Better Scalability** - Microservices architecture
✅ **Advanced Analytics** - Optimize with ML insights
✅ **Cloud-Native** - Kubernetes-ready
✅ **Modern Stack** - Latest Camunda features
✅ **Future-Proof** - Active development and support

## Next Steps

1. **Deploy AI-Enhanced Workflows**
   - See `CAMUNDA_8_AI_FEATURES.md`
   - Use OpenAI connector for intelligent decisions

2. **Set Up Monitoring**
   - Configure Optimize dashboards
   - Enable process mining
   - Track AI performance

3. **Train Team**
   - Learn Zeebe concepts
   - Practice with Modeler 8
   - Understand job workers

4. **Optimize Performance**
   - Tune Elasticsearch
   - Configure Zeebe partitions
   - Monitor resource usage

## Support & Resources

- **Official Docs**: https://docs.camunda.io
- **Community Forum**: https://forum.camunda.io
- **AI Features Guide**: `./CAMUNDA_8_AI_FEATURES.md`
- **Migration Tool**: https://github.com/camunda/camunda-7-to-8-migration

---

**Upgrade Completed**: September 5, 2026
**Status**: ✅ Camunda 8.7 with AI Features Active
