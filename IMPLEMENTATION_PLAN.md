# Loan Collection System Implementation Plan
## GenAI + Camunda 8 (BPMN + DMN) Integration Architecture

---

## 1. Project Overview

**System Name**: Post-Loan Collection System with GenAI Integration (貸後催收系統)

**Target Market**: Hong Kong SAR (initial focus). Compliance alignment: **Money Lenders Ordinance (Cap. 163)**, **Personal Data (Privacy) Ordinance (Cap. 486 / PDPO)**, **Code of Money Lending Practice** (published by the Licensed Money Lenders Association), **Guidelines on Licensing Conditions of Money Lenders** (Registrar of Money Lenders / Companies Registry), and the **Code of Banking Practice** (HKMA/HKAB).

**Core Principle**: Camunda 8 DMN handles deterministic, auditable rules (compliance, hard thresholds); GenAI handles understanding, generation, and soft decisions. The two are connected by a **trust gate**: high-confidence, low-risk outputs auto-execute; lower-confidence or higher-risk outputs route to human review; and Camunda DMN always performs the final hard-compliance validation that GenAI cannot override.

**Technology Stack**:
- **Frontend**: Next.js 14+ (App Router, TypeScript)
- **Backend**: Python 3.11+ with FastAPI + uv (package manager)
- **Rules Engine**: Camunda 8 **DMN** (built-in, no separate Drools service — deliberate for demo scope)
- **BPMN Engine**: Camunda 8 or jBPM (containerized with Docker)
               - **Message Queue**: RabbitMQ or Apache Kafka (async task processing)
- **GenAI**: LLM integration (OpenAI/Anthropic/Local models) + RAG
- **Database**: PostgreSQL (main), Redis (cache), Vector DB (embeddings)
- **Infrastructure**: Docker + Docker Compose (dev), Kubernetes (production)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend Layer (Next.js)                   │
│  - Collection Dashboard  - Rule Editor  - Case Management        │
│  - Script Templates     - Compliance Monitor  - Analytics        │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST/GraphQL API
┌────────────────────────┴────────────────────────────────────────┐
│                    API Gateway (FastAPI)                         │
│  - Authentication  - Rate Limiting  - Request Routing            │
└────────┬───────────────────────────┬────────────────────────────┘
         │                           │
    ┌────┴─────┐              ┌─────┴──────────────┐
    │  GenAI   │              │  Camunda 8         │
    │ Service  │              │  (BPMN + DMN)      │
    │ (Python) │              │  Zeebe + Connectors│
    └────┬─────┘              └─────┬──────────────┘
         │                           │
         └────────┬──────────────────┘
                  │
    ┌─────────────┴──────────────────────────┐
    │   Message Queue (RabbitMQ/Kafka)       │
    │   - Async GenAI tasks                  │
    │   - Camunda → GenAI external tasks     │
    └─────────────┬──────────────────────────┘
                  │
    ┌─────────────┴──────────────────────────┐
    │      Data Layer                        │
    │  PostgreSQL │ Redis │ Vector DB        │
    │  (Camunda uses PostgreSQL for state)   │
    └────────────────────────────────────────┘
```

---

## 3. Component Breakdown

### 3.1 Frontend (Next.js)

**Structure**:
```
loan-agent-frontend/
├── app/
│   ├── (dashboard)/
│   │   ├── cases/              # Case management
│   │   ├── rules/              # Visual rule editor
│   │   ├── scripts/            # Script templates
│   │   ├── analytics/          # Performance metrics
│   │   └── compliance/         # Compliance monitoring
│   ├── api/                    # API routes (BFF pattern)
│   └── auth/                   # Authentication pages
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── features/
│   │   ├── rule-builder/       # Visual decision table builder
│   │   ├── script-editor/      # Script template editor
│   │   ├── case-timeline/      # Case history visualization
│   │   └── genai-copilot/      # AI assistant widget
│   └── charts/                 # Analytics charts
├── lib/
│   ├── api/                    # API client
│   ├── hooks/                  # React hooks
│   └── utils/                  # Utilities
└── types/                      # TypeScript definitions
```

**Key Features**:
- Server-side rendering for dashboard performance
- Real-time updates via WebSocket/Server-Sent Events
- Visual decision table editor (drag-and-drop)
- Natural language rule input interface
- Case summary and timeline view
- Compliance alert dashboard
- A/B testing comparison views

**UI Libraries**:
- shadcn/ui (component library)
- TanStack Table (data grids)
- Recharts (analytics)
- React Flow (rule visualization)
- Lexical/Slate (rich text editor for scripts)

---

### 3.2 Backend (FastAPI + Python)

**Structure**:
```
loan-agent-backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── cases.py        # Case management endpoints
│   │   │   ├── rules.py        # Rule CRUD
│   │   │   ├── scripts.py      # Script templates
│   │   │   ├── genai.py        # GenAI endpoints
│   │   │   └── analytics.py    # Reporting
│   │   └── deps.py             # Dependencies
│   ├── core/
│   │   ├── config.py           # Settings
│   │   ├── security.py         # Auth
│   │   └── logging.py          # Logging
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/
│   │   ├── genai/
│   │   │   ├── llm_client.py   # LLM wrapper
│   │   │   ├── rag_service.py  # RAG pipeline
│   │   │   ├── intent_classifier.py
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── script_generator.py
│   │   │   └── summarizer.py
│   │   ├── camunda/
│   │   │   ├── client.py        # Camunda 8 REST API wrapper
│   │   │   └── workers/         # External-task workers (pyzeebe)
│   │   └── trust_gate.py       # Confidence threshold logic
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   └── utils/
│       ├── validators.py
│       └── formatters.py
├── tests/
├── alembic/                    # Database migrations
├── pyproject.toml              # uv config
└── Dockerfile
```

**Key Responsibilities**:
- RESTful API endpoints
- GenAI service orchestration
- Camunda 8 BPMN/DMN orchestration + External Task integration
- Trust gate implementation (confidence scoring)
- Audit trail logging
- Background task processing (Celery/RQ)

**Python Packages** (managed by `uv`):
- `fastapi` + `uvicorn`
- `sqlalchemy` + `alembic`
- `pydantic` v2
- `openai` / `anthropic` (LLM clients)
- `langchain` (RAG, agents)
- `chromadb` / `qdrant-client` (vector DB)
- `pyzeebe` (Python External Task worker for Camunda 8)
- `redis`
- `celery` (async tasks) or `arq` (async task queue)
- `aio-pika` (RabbitMQ async client) or `aiokafka` (Kafka async client)
- `httpx` (async HTTP)

---

### 3.3 Decision Rules with Camunda DMN

**Approach**: Rules are authored as **DMN (Decision Model and Notation)** decision tables inside Camunda 8's Web Modeler, evaluated by Camunda's Zeebe engine at runtime. **No separate rules microservice** — DMN lives alongside BPMN in the same Camunda 8 deployment.

**Why DMN instead of Drools for the demo**:
- One fewer service to deploy (just Camunda).
- Decision tables are visually editable in Web Modeler and business-readable — credible to non-technical stakeholders.
- DMN uses **FEEL** (Friendly Enough Expression Language) for hit policies — simpler to learn than DRL.
- Every demo rule below (red lines, assignment, strategy) fits DMN cleanly:
  - Hit policy `FIRST` / `PRIORITY` for assignment and strategy.
  - Hit policy `UNIQUE` / `COLLECT` for red-line compliance checks.
- Triggered from BPMN via a **Business Rule Task** — single BPMN process can invoke DMN inline.

**Trade-offs accepted**:
- No complex forward-chaining (Rete salience, `accumulate` patterns, multi-source stateful joins) — not needed for demo scope.
- If a real production rollout eventually needs that complexity, add Drools back as a sidecar; the BPMN abstraction stays the same.

**DMN Artefacts (authored in Web Modeler)**:
```
camunda-models/
├── dmn/
│   ├── red-line-compliance.dmn    # 催收紅線決策表
│   ├── case-priority.dmn          # 案件優先級
│   ├── case-assignment.dmn        # 分案規則
│   ├── contact-strategy.dmn       # 聯絡策略
│   └── escalation-rules.dmn       # 升級規則
└── bpmn/
    ├── case-intake.bpmn
    ├── contact-strategy.bpmn
    └── compliance-check.bpmn
```

**Example: `red-line-compliance.dmn` (decision table excerpt)**

| Input 1 | Input 2 | Input 3 | Output |
|---|---|---|---|
| Contact time | Contact type | Collector identified? | Allowed |
| 08:00–21:00 | SMS / email / call | Yes | ✅ allowed |
| 08:00–21:00 | SMS / email / call | No | ❌ block — no_collector_identification |
| 21:01–07:59 | any | any | ❌ block — outside_contact_hours |
| any | third-party | debt disclosed | ❌ block — third_party_disclosure |
| any | any | harassing language detected | ❌ block — harassment |

**Deployment**: DMN models are packaged with the Camunda 8 process bundle and loaded on deploy — no separate Maven/Gradle build. Versioned in Git.

---

### 3.4 Camunda 8 (BPMN + DMN + Connectors)

**Choice**: **Camunda 8 (Zeebe-based)** — the only workflow/rules engine for this demo. No jBPM, no Drools.

**Why Camunda 8**:
- BPMN 2.0 + DMN + Connectors + Operate/Tasklist/Optimize — all in one platform.
- Cloud-native: Zeebe engine scales horizontally, runs well in K8s (the demo target).
- **AI-ready Connectors** — pre-built connectors for OpenAI, Bedrock, Anthropic, HTTP; or just register your GenAI service as a custom REST connector.
- **External Task pattern** lets your Python FastAPI act as a worker pulling tasks from Camunda — same pattern as the Service Task interface in §3.5.
- DMN decision tables are modelable in Web Modeler and business-readable.
- Community Edition is free and sufficient for this demo + pilot (Enterprise adds multi-region clustering, advanced Optimize, SSO).

**Docker Compose (Camunda 8 + Self-Managed)**:
```yaml
# docker-compose.yml
services:
  camunda:
    image: camunda/camunda-platform:latest
    ports:
      - "8080:8080"   # Operate
      - "8081:8081"   # Tasklist
      - "26500:26500" # gRPC gateway (for workers)
    environment:
      - CAMUNDA_OPERATE_ZEEBE_GATEWAYADDRESS=zeebe:26500
      - ZEEBE_BROKER_EXPORTERS_CAMUNDAEXPORTER_CLASSNAME=io.camunda.exporter.CamundaExporter
    depends_on:
      - postgres
      - zeebe

  zeebe:
    image: camunda/zeebe:latest
    ports:
      - "26500:26500"
    environment:
      - ZEEBE_BROKER_CLUSTER_SIZE=1
      - ZEEBE_BROKER_PARTITIONS_COUNT=1
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: camunda
      POSTGRES_USER: camunda
      POSTGRES_PASSWORD: camunda
    volumes:
      - camunda_pg:/var/lib/postgresql/data

  # GenAI service (unchanged)
  genai:
    build: ./genai-service
    ports:
      - "8001:8001"

volumes:
  camunda_pg:
```

**BPMN Processes (authored in Web Modeler)**:
1. **Case Intake Workflow**: new case → DMN `case-priority` → DMN `case-assignment` → queue
2. **Contact Strategy Workflow**: case → GenAI service task (external task worker) → DMN `red-line-compliance` → trust-gate gateway → execute | human review | block
3. **Compliance Check Workflow**: action → DMN `red-line-compliance` → allow/block + log
4. **Dispute Resolution**: customer message → GenAI intent classification → user task → resolution

**Worker integration**: Python FastAPI workers register as External Task clients to Camunda using the `pyzeebe` library (or the generic zeebe-gRPC client). Workers expose `POST /genai/*` endpoints; Camunda invokes them when a Service Task with type `genai-*` arrives.

---

### 3.5 GenAI Service Layer

**Architecture**:
```
┌─────────────────────────────────────────────┐
│          GenAI Service (FastAPI)             │
├─────────────────────────────────────────────┤
│  API Endpoints                               │
│  - /genai/summarize                          │
│  - /genai/generate-script                    │
│  - /genai/analyze-intent                     │
│  - /genai/score-willingness                  │
│  - /genai/generate-rule (NL → DMN)           │
│  - /genai/compliance-check                   │
└───────────┬─────────────────────────────────┘
            │
    ┌───────┴────────┐
    │   LLM Client   │ (OpenAI/Anthropic/Local)
    └───────┬────────┘
            │
    ┌───────┴────────┐
    │   RAG Pipeline │
    └───────┬────────┘
            │
    ┌───────┴──────────────────────────┐
    │  Knowledge Base (Vector DB)       │
    │  - Compliance policies            │
    │  - Script templates               │
    │  - Historical cases               │
    │  - Regulations                    │
    │  - Successful strategies          │
    └───────────────────────────────────┘
```

**RAG Implementation**:
- Embedding model: OpenAI `text-embedding-3-large` or local BAAI/bge
- Vector DB: ChromaDB (dev) / Qdrant (production)
- Chunking strategy: Semantic chunking (LangChain)
- Retrieval: Hybrid search (vector + keyword)
- Re-ranking: Cross-encoder model

**HK Compliance Knowledge Base (RAG Sources)** — the authoritative Hong Kong documents to ingest (stored under `rag/knowledge_base/` and embedded into the `compliance_policies` vector collection):

| # | Document | Authority | Use in RAG |
|---|----------|-----------|------------|
| 1 | Money Lenders Ordinance (Cap. 163) | HKSAR e-Legislation | Statutory basis for licensed money-lending; offences, interest caps, licensing |
| 2 | Personal Data (Privacy) Ordinance (Cap. 486 / PDPO) | PCPD | Data Protection Principles (DPP1–6) — lawful collection, purpose limitation, retention, security, access |
| 3 | Code of Money Lending Practice | Licensed Money Lenders Association (LMLA) | **Industry conduct code** — this is the primary source for the red-line contact rules (see §10.2) |
| 4 | Guidelines on Licensing Conditions of Money Lenders | Registrar of Money Lenders (Companies Registry) | Licensing conditions and regulatory expectations |
| 5 | Code of Banking Practice | HKMA / HKAB | Fair treatment of customers, debt collection conduct for banks |
| 6 | CLIC "Debt Collection" plain-language summary | Community Legal Information Centre | Human-readable grounding for what constitutes harassment/unlawful collection |

**HK red lines these documents encode** (must be reflected verbatim in Camunda DMN decision tables and RAG citations):
- Debt collectors must **identify themselves and state the purpose** of the call.
- **No contacting third parties** (family, friends, employers, referees) to press for payment or to disclose the debt, **unless** that party is legally liable (e.g., a guarantor) or is an employer contacted only for a permitted purpose such as locating the borrower.
- **No harassment or intimidation** — no threats of violence, no abusive/threatening language, no excessive/unreasonable contact.
- Contact only at **reasonable hours** and with **reasonable frequency** (the Code of Money Lending Practice does not prescribe a single hard hour range, so this is configured as a Camunda DMN parameter — default 08:00–21:00 — that compliance officers can tune).
- **No misrepresentation** — collectors must not falsely claim to be law enforcement, a court, or a credit-reference agency, and must not imply arrest/imprisonment.
- **Data privacy** — personal data handled per PDPO DPPs; no disclosure of debt details to unauthorized parties.

**Trust Gate Logic**:
```python
class TrustGate:
    def evaluate(self, genai_output: dict) -> Decision:
        confidence = genai_output.get("confidence", 0.0)
        risk_level = self.assess_risk(genai_output)
        
        if confidence >= 0.9 and risk_level == "low":
            return Decision.AUTO_EXECUTE
        elif confidence >= 0.7 and risk_level == "medium":
            return Decision.HUMAN_REVIEW
        else:
            return Decision.ESCALATE
    
    def assess_risk(self, output: dict) -> str:
        # Based on case amount, customer segment, action type
        if output["amount"] > 100000:
            return "high"
        elif output["action"] == "legal_action":
            return "high"
        elif output["customer_segment"] == "VIP":
            return "medium"
        return "low"
```

---

### 3.6 Message Queue Layer

**Choice**: **RabbitMQ** (simpler, good for task queues) vs **Apache Kafka** (better for event streaming, higher throughput)

**Recommendation**: Start with **RabbitMQ** for simplicity, migrate to Kafka if event streaming needed at scale.

**Use Cases**:

1. **Long-running GenAI Completions**:
   - Large batch summarizations (100+ cases)
   - Complex rule generation with validation
   - Multi-document analysis
   - Strategy optimization jobs

2. **Async Service Communication**:
   - GenAI → Camunda DMN validation requests
   - BPMN → External task workers
   - Notification delivery (email, SMS)

3. **Event-Driven Workflows**:
   - Case status changes
   - Compliance violation alerts
   - Real-time dashboard updates

**Architecture Pattern**:

```
Producer (FastAPI)                    Consumer (Worker)
      │                                     │
      │  1. Submit GenAI task               │
      ├────────────────────────────────────>│
      │     (with task_id)                  │
      │                                     │
      │  2. Return task_id immediately      │
      │     (HTTP 202 Accepted)             │
      │                                     │
      │                                3. Process task
      │                                     │
      │                                4. Update DB/Redis
      │                                     │
      │  5. Poll/WebSocket for result       │
      │<────────────────────────────────────│
```

**Queue Structure**:

**RabbitMQ Exchanges & Queues**:
```
Exchanges:
  - genai.tasks (direct)
  - genai.results (topic)
  - dmn.evaluation (direct)
  - notifications (fanout)

Queues:
  - genai.summarize
  - genai.script_generation
  - genai.rule_generation
  - genai.batch_processing
  - dmn.compliance_evaluate
  - notifications.email
  - notifications.sms
```

**Message Format**:
```python
# Task message
{
    "task_id": "uuid",
    "task_type": "summarize|script_gen|rule_gen",
    "priority": 1-10,
    "payload": {
        "case_id": "uuid",
        "options": {...}
    },
    "callback_url": "https://api/callbacks/task/{task_id}",
    "retry_count": 0,
    "timeout": 300  # seconds
}

# Result message
{
    "task_id": "uuid",
    "status": "completed|failed|timeout",
    "result": {...},
    "error": "...",
    "completed_at": "2026-09-02T10:30:00Z",
    "execution_time_ms": 2500
}
```

**Implementation Example**:

```python
# services/mq/rabbitmq_client.py
import aio_pika
import json
from typing import Any, Callable

class MessageQueueClient:
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
    
    async def publish_task(
        self,
        queue_name: str,
        task_data: dict,
        priority: int = 5
    ) -> str:
        """Publish task to queue, return task_id"""
        task_id = str(uuid.uuid4())
        message = {
            "task_id": task_id,
            "payload": task_data,
            "priority": priority,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                priority=priority,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )
        
        return task_id
    
    async def consume_tasks(
        self,
        queue_name: str,
        handler: Callable
    ):
        """Consume tasks from queue"""
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-max-priority": 10}
        )
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    task_data = json.loads(message.body.decode())
                    try:
                        result = await handler(task_data)
                        await self.publish_result(
                            task_data["task_id"],
                            result,
                            "completed"
                        )
                    except Exception as e:
                        await self.publish_result(
                            task_data["task_id"],
                            {"error": str(e)},
                            "failed"
                        )
    
    async def publish_result(
        self,
        task_id: str,
        result: Any,
        status: str
    ):
        """Publish task result"""
        exchange = await self.channel.declare_exchange(
            "genai.results",
            aio_pika.ExchangeType.TOPIC
        )
        
        message_body = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        await exchange.publish(
            aio_pika.Message(body=json.dumps(message_body).encode()),
            routing_key=f"result.{status}"
        )


# Worker process (separate from API server)
# workers/genai_worker.py
async def process_summarization_task(task_data: dict) -> dict:
    """Worker handler for summarization tasks"""
    case_id = task_data["payload"]["case_id"]
    
    # Fetch case data
    case = await get_case(case_id)
    
    # Generate summary
    genai_service = SummarizerService()
    summary = await genai_service.summarize(case)
    
    # Store in DB
    await save_summary(case_id, summary)
    
    return {
        "case_id": case_id,
        "summary": summary,
        "confidence": summary.get("confidence", 0.0)
    }

async def main():
    mq = MessageQueueClient(settings.RABBITMQ_URL)
    await mq.connect()
    
    # Start consuming tasks
    await mq.consume_tasks(
        "genai.summarize",
        process_summarization_task
    )

if __name__ == "__main__":
    asyncio.run(main())
```

**API Integration**:

```python
# api/v1/genai.py
@router.post("/summarize/async")
async def summarize_async(
    case_id: str,
    mq: MessageQueueClient = Depends(get_mq_client)
) -> dict:
    """Submit async summarization task"""
    
    task_id = await mq.publish_task(
        queue_name="genai.summarize",
        task_data={"case_id": case_id},
        priority=5
    )
    
    # Store task status in Redis
    await redis_client.setex(
        f"task:{task_id}:status",
        3600,  # 1 hour TTL
        "pending"
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "status_url": f"/api/v1/tasks/{task_id}"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    redis: Redis = Depends(get_redis)
) -> dict:
    """Check task status"""
    
    status = await redis.get(f"task:{task_id}:status")
    
    if not status:
        raise HTTPException(404, "Task not found")
    
    if status == "completed":
        result = await redis.get(f"task:{task_id}:result")
        return {
            "task_id": task_id,
            "status": "completed",
            "result": json.loads(result)
        }
    
    return {
        "task_id": task_id,
        "status": status
    }
```

**Frontend Integration (Polling)**:

```typescript
// lib/api/tasks.ts
export async function submitAsyncTask(
  endpoint: string,
  payload: any
): Promise<string> {
  const response = await fetch(`/api/v1/${endpoint}/async`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  return data.task_id;
}

export async function pollTaskStatus(
  taskId: string,
  onComplete: (result: any) => void,
  onError: (error: string) => void
) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/v1/tasks/${taskId}`);
    const data = await response.json();
    
    if (data.status === 'completed') {
      clearInterval(interval);
      onComplete(data.result);
    } else if (data.status === 'failed') {
      clearInterval(interval);
      onError(data.error);
    }
  }, 2000); // Poll every 2 seconds
}

// Usage in component
const handleSummarize = async () => {
  const taskId = await submitAsyncTask('genai/summarize', { case_id: '123' });
  
  await pollTaskStatus(
    taskId,
    (result) => setSummary(result.summary),
    (error) => showError(error)
  );
};
```

**Alternative: WebSocket for Real-time Updates**:

```python
# api/v1/websocket.py
@router.websocket("/ws/tasks/{task_id}")
async def websocket_task_status(
    websocket: WebSocket,
    task_id: str,
    redis: Redis = Depends(get_redis)
):
    await websocket.accept()
    
    # Subscribe to Redis pub/sub for task updates
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"task:{task_id}:updates")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)
                
                if data["status"] in ["completed", "failed"]:
                    break
    finally:
        await pubsub.unsubscribe(f"task:{task_id}:updates")
        await websocket.close()
```

**Monitoring & Dead Letter Queue**:

```python
# Setup dead letter queue for failed tasks
async def setup_dlq():
    # Main queue with DLQ
    await channel.declare_queue(
        "genai.summarize",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "genai.summarize.failed",
            "x-message-ttl": 300000,  # 5 min timeout
            "x-max-retries": 3
        }
    )
    
    # Dead letter queue
    await channel.declare_queue(
        "genai.summarize.failed",
        durable=True
    )
```

**Performance Considerations**:

- **Throughput**: RabbitMQ ~10k-50k msg/s, Kafka ~100k-1M msg/s
- **Latency**: RabbitMQ ~1-5ms, Kafka ~5-10ms
- **Persistence**: Both support durable queues
- **Ordering**: Kafka guarantees per-partition order, RabbitMQ per-queue
- **Scaling**: Kafka better for high-volume event streaming

**When to Use Each**:

| Scenario | Recommendation |
|----------|----------------|
| Task queues (GenAI jobs) | RabbitMQ |
| Request-response patterns | RabbitMQ |
| Event streaming (audit logs) | Kafka |
| Real-time analytics | Kafka |
| High throughput (>100k msg/s) | Kafka |
| Simple setup | RabbitMQ |

---

## 4. Database Design

### 4.1 PostgreSQL Schema

**Core Tables**:
```sql
-- Cases
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    loan_id VARCHAR(50) NOT NULL,
    overdue_days INTEGER,
    overdue_amount DECIMAL(15,2),
    status VARCHAR(20),
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Contact History
CREATE TABLE contact_history (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    contact_type VARCHAR(20), -- call, sms, email
    contact_time TIMESTAMP,
    transcript TEXT,
    sentiment VARCHAR(20),
    intent VARCHAR(50),
    outcome VARCHAR(50),
    created_by UUID
);

-- Rules
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    rule_type VARCHAR(30), -- compliance, assignment, strategy
    drl_content TEXT,
    decision_table_path VARCHAR(255),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    version INTEGER
);

-- GenAI Outputs (Audit Trail)
CREATE TABLE genai_audit (
    id UUID PRIMARY KEY,
    case_id UUID,
    service_type VARCHAR(50), -- summarize, script_gen, intent
    input_data JSONB,
    output_data JSONB,
    confidence FLOAT,
    trust_gate_decision VARCHAR(20),
    human_review_result VARCHAR(20),
    reviewed_by UUID,
    created_at TIMESTAMP
);

-- Scripts/Templates
CREATE TABLE script_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    scenario VARCHAR(50),
    content TEXT,
    compliance_validated BOOLEAN,
    usage_count INTEGER,
    effectiveness_score FLOAT
);

-- Compliance Violations
CREATE TABLE compliance_violations (
    id UUID PRIMARY KEY,
    case_id UUID,
    contact_id UUID,
    violation_type VARCHAR(50),
    description TEXT,
    severity VARCHAR(20),
    detected_by VARCHAR(20), -- dmn, genai, human
    detected_at TIMESTAMP,
    resolved BOOLEAN
);
```

### 4.2 Redis Cache

**Usage**:
- Session storage
- Rate limiting counters
- Real-time contact frequency tracking
- GenAI response cache (for repeated queries)

**Key Patterns**:
```
case:{case_id}:summary
case:{case_id}:contact_count:{date}
genai:cache:{hash}
rule:{rule_id}:compiled
```

### 4.3 Vector Database

**Collections**:
- `compliance_policies` (regulations, red-line rules)
- `script_templates` (successful scripts with metadata)
- `case_history` (historical case summaries for RAG)
- `customer_objections` (common objections + responses)

---

## 5. API Design

### 5.1 Backend API (FastAPI)

**Authentication**: JWT Bearer tokens

**Key Endpoints**:

```
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

# Cases
GET    /api/v1/cases
GET    /api/v1/cases/{id}
POST   /api/v1/cases
PATCH  /api/v1/cases/{id}
GET    /api/v1/cases/{id}/timeline
POST   /api/v1/cases/{id}/assign

# GenAI
POST   /api/v1/genai/summarize
POST   /api/v1/genai/generate-script
POST   /api/v1/genai/analyze-intent
POST   /api/v1/genai/score-willingness
POST   /api/v1/genai/generate-rule
POST   /api/v1/genai/compliance-check

# Rules
GET    /api/v1/rules
POST   /api/v1/rules
PUT    /api/v1/rules/{id}
DELETE /api/v1/rules/{id}
POST   /api/v1/rules/validate
POST   /api/v1/rules/detect-conflicts

# Workflows (BPMN)
POST   /api/v1/workflows/start
GET    /api/v1/workflows/{id}/status
POST   /api/v1/workflows/{id}/complete-task

# Analytics
GET    /api/v1/analytics/performance
GET    /api/v1/analytics/compliance-metrics
GET    /api/v1/analytics/ab-test-results
```

### 5.2 Camunda 8 API (DMN + BPMN)

DMN models are evaluated inside Camunda — no separate API needed. FastAPI only calls Camunda's Deployments + Process-Instance REST API.

```
# Deploy a DMN model (called once on boot / rule update)
POST   /v1/deployments                   (multipart: dmn.xml)
POST   /v1/deployments                   (multipart: bpmn.xml)

# Trigger a process instance from Next.js / FastAPI
POST   /v1/process-instances             { processDefinitionId, variables }

# Operate on a running instance (admin / supervisor UI)
GET    /v1/process-instances/{key}
POST   /v1/process-instances/{key}/migration

# Human tasks (Tasklist)
GET    /v1/tasks                         (?assignee=...)
POST   /v1/tasks/{id}/complete           { variables }
```

DMN evaluation itself happens server-side inside Zeebe via Business Rule Tasks in the BPMN model — there is no separate `/dmn/evaluate` endpoint to call from FastAPI.

---

## 6. Integration Points

### 6.1 FastAPI ↔ Camunda 8

**Approach**: Two complementary patterns.

**A. Camunda calls FastAPI (Camunda as the orchestrator)**

GenAI work happens in Python FastAPI; Camunda invokes it through the **External Task** pattern (Python workers pull jobs from Camunda via `pyzeebe`).

```python
# workers/genai_worker.py
from pyzeebe import ZeebeClient, ZeebeWorker, Job

zeebe = ZeebeClient(hostname="camunda", port=26500)
worker = ZeebeWorker(zeebe)

@worker.task(task_type="genai_summarize")
async def summarize(job: Job) -> dict:
    case_id = job.variables["case_id"]
    summary = await genai_service.summarize(case_id)
    return {"summary": summary, "confidence": summary["confidence"]}

@worker.task(task_type="genai_generate_script")
async def generate_script(job: Job) -> dict:
    case = job.variables["case"]
    script = await genai_service.generate_script(case)
    return {"script": script["text"], "confidence": script["confidence"]}
```

**B. FastAPI calls Camunda (FastAPI as the API gateway)**

For orchestrating a process from the Next.js UI (e.g., "start intake process for this case"), FastAPI uses the Camunda 8 REST API.

```python
# services/camunda/client.py
import httpx

class CamundaClient:
    def __init__(self, base_url: str = "http://camunda:8080"):
        self.base_url = base_url

    async def start_process(self, bpmn_process_id: str, variables: dict) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v1/process-instances",
                json={"processDefinitionId": bpmn_process_id, "variables": variables},
            )
            return r.json()["processInstanceKey"]
```

**DMN evaluation**: handled entirely inside Camunda (BPMN Business Rule Task) — no FastAPI code needed.

### 6.3 BPMN Orchestration

**Example Workflow** (Camunda BPMN XML excerpt):
```xml
<bpmn:process id="case-assignment-process">
  <bpmn:startEvent id="StartEvent_1"/>
  <bpmn:serviceTask id="GenAI_Score"
                    name="GenAI Willingness Scoring"
                    zeebe:TaskDefinition type="genai_score_willingness"/>
  <bpmn:businessRuleTask id="DMN_Assign"
                         name="Camunda DMN: Case Assignment"
                         zeebe:TaskDefinition type="DMN"
                         zeebe:DecisionRef="case-assignment"/>
  <bpmn:businessRuleTask id="DMN_RedLine"
                         name="Camunda DMN: HK Red-line Compliance"
                         zeebe:TaskDefinition type="DMN"
                         zeebe:DecisionRef="red-line-compliance"/>
  <bpmn:exclusiveGateway id="TrustGate">
    <bpmn:conditionExpression>
      ${confidence >= 0.8}
    </bpmn:conditionExpression>
  </bpmn:exclusiveGateway>
  <bpmn:userTask id="HumanReview" name="Manual Review"/>
  <bpmn:endEvent id="EndEvent_1"/>
</bpmn:process>
```

**Delegates** (Java/Python workers — note: DMN decision tables above are evaluated by Zeebe directly, so no Java delegate is required for those steps):
- `GenAIScoreDelegate`: Calls FastAPI GenAI endpoint
- Workers can be Python (using Camunda external task pattern); all decisions are handled by Camunda DMN Business Rule Tasks, not Java delegates
- If a step must call out to an external system (e.g. notify a collections agency, write to a CRM), implement it as a Camunda External Task worker in FastAPI via `pyzeebe`

---

## 7. Development Phases

### Phase 0: Foundation (Week 1-4)

**Goals**: Set up infrastructure, base architecture

**Tasks**:
1. Initialize repositories:
   ```bash
   mkdir loan-agent-frontend loan-agent-backend camunda-models
   cd loan-agent-frontend && npx create-next-app@latest .
   cd ../loan-agent-backend && uv init
   ```

2. Docker Compose environment:
   - PostgreSQL + Redis + Camunda/jBPM
   - Development containers for all services

3. Database schema creation:
   - Alembic migrations for Python
   - Flyway migrations for Java

4. Authentication setup:
   - JWT implementation in FastAPI
   - Next.js middleware for protected routes

5. CI/CD pipeline skeleton:
   - GitHub Actions / GitLab CI
   - Linting, testing, building

**Deliverables**:
- All services running via `docker-compose up`
- Basic health check endpoints
- Empty frontend with auth flow
- Database migrations

---

### Phase 1: Core Case Management (Week 5-8)

**Goals**: Basic case CRUD, Camunda DMN integration, simple rules

**Tasks**:
1. **Backend**:
   - Case management API
   - Contact history tracking
   - Camunda DMN deployment via REST API

2. **Frontend**:
   - Case list/detail pages
   - Timeline view
   - Basic search/filter

3. **Camunda DMN**:
   - Simple assignment rules
   - Compliance red-line rules (time window, frequency)
   - Decision table import

4. **BPMN**:
   - Case intake workflow
   - Assignment workflow

**Deliverables**:
- Collectors can view/manage cases
- Basic rule execution via Camunda DMN
- Workflow automation for case routing

---

### Phase 2: GenAI - Assistive Features (Week 9-12)

**Goals**: Low-risk GenAI features (summary, Copilot)

**Tasks**:
1. **GenAI Service**:
   - LLM client wrapper
   - Case summarization
   - Script generation (with human review)
   - Intent classification

2. **RAG Setup**:
   - Vector DB initialization
   - Compliance policy embedding
   - Script template indexing

3. **Frontend**:
   - GenAI Copilot widget
   - Script editor with AI suggestions
   - Case summary generation button

4. **Audit Trail**:
   - Log all GenAI calls to `genai_audit` table
   - Confidence scores displayed to users

**Deliverables**:
- Collectors get AI-generated case summaries
- Script drafts via AI (human confirms before use)
- Full audit trail

---

### Phase 3: Natural Language Rule Generation (Week 13-16)

**Goals**: NL → DMN (with HK compliance RAG grounding), solve pain points 1 & 3

**Tasks**:
1. **Rule Generator**:
   - Prompt engineering for DMN table generation (inputs/outputs/hit policy)
   - Few-shot examples grounded in the HK RAG knowledge base (Cap. 163, PDPO, LMLA Code)
   - Validation: every generated rule must cite a retrieved clause from the RAG KB
   - FEEL expression syntax checks

2. **Frontend**:
   - Natural language rule input form (Chinese / English)
   - Preview generated DMN decision table (rendered in Web Modeler-style view)
   - Approve/reject workflow; on approve, deploy via Camunda 8 REST API

3. **Camunda Integration**:
   - DMN versioning through Camunda's deployment API
   - Conflict detection by DMN consistency checker (overlap / gap analysis)
   - Rollback to previous DMN version if a new deploy causes regressions

**Deliverables**:
- Business users describe a rule in plain language
- System retrieves relevant HK compliance clauses, generates DMN decision table, shows preview with citations
- Compliance officer approves → DMN deploys live in Camunda 8
- Every active rule carries an audit-trail citation back to its source clause

---

### Phase 4: Decision Support (Week 17-22)

**Goals**: GenAI-powered scoring, strategy recommendation

**Tasks**:
1. **Scoring Models**:
   - Willingness-to-pay scoring
   - Contact strategy recommendation
   - Optimal channel/time prediction

2. **Trust Gate**:
   - Implement confidence thresholds
   - Risk-based routing (auto vs. human review)

3. **Camunda Integration**:
   - GenAI scores as input facts to DMN tables
   - DMN applies hard constraints (HK red lines)
   - Combined decision output

4. **A/B Testing**:
   - Strategy assignment (control vs. GenAI-recommended)
   - Performance tracking

**Deliverables**:
- Cases get AI-generated willingness scores
- Strategies recommended by AI, validated by Camunda DMN
- High-confidence actions auto-execute (low-risk cases)
- A/B test framework live

---

### Phase 5: Automation & Quality Assurance (Week 23-28)

**Goals**: Auto QA, compliance monitoring, chatbot

**Tasks**:
1. **Automated Quality Check**:
   - Call transcript analysis (all calls, not samples)
   - Compliance violation detection
   - Risk scoring

2. **Intelligent Chatbot**:
   - Customer-facing collection bot (SMS/App)
   - Intent-based conversation flow
   - Escalation to human when needed

3. **Compliance Dashboard**:
   - Real-time violation alerts
   - Drill-down by collector/case
   - Trend analysis

4. **Skip Tracing**:
   - Contact relationship extraction from history
   - AI-suggested outreach strategies

**Deliverables**:
- 100% call quality check (vs. previous sampling)
- Chatbot handles routine follow-ups
- Compliance violations caught in real-time
- Contact recovery rate improves

---

### Phase 6: Optimization Loop (Week 29+, Ongoing)

**Goals**: Continuous learning, strategy refinement

**Tasks**:
1. **Analytics**:
   - Strategy effectiveness attribution
   - Cohort analysis (GenAI vs. traditional)
   - Rule performance monitoring

2. **Feedback Loop**:
   - GenAI retraining on successful cases
   - Rule library updates based on outcomes
   - Script template evolution

3. **Advanced Features**:
   - Multi-agent debate (multiple LLMs vote on strategy)
   - Personalization engine (per-customer adaptation)
   - Predictive default modeling

**Deliverables**:
- Monthly strategy review reports
- Automated rule/script optimization
- Continuous performance improvement

---

## 8. Demo Data Generator

**Purpose**: Generate realistic demo data for Capco and executive presentations, showcasing the full system capabilities with representative scenarios.

> **Hong Kong market localization** (align with the Cap. 163 / PDPO target market): the generator defaults below are mainland-China flavoured and must be switched to HK conventions before a client-facing demo:
> - **Names**: Cantonese/English names (e.g., 陳大文 / Chan Tai Man) instead of mainland pinyin-style names.
> - **Identity**: HKID number format (`A123456(7)`) instead of the 18-digit mainland ID card.
> - **Phone**: `+852` mobile numbers (prefix `5`/`6`/`9`, 8 digits) instead of `13x`/`15x`/`18x`; SMS sender uses an HK short code, not `400-123-4567`.
> - **Addresses**: HK districts (Central, Tsim Sha Tsui, Mong Kok, Sha Tin, Tsuen Wan, etc.) instead of Beijing/Shanghai/Guangdong.
> - **Currency**: HKD (`HK$`) instead of `元`/RMB.
> - **Scripts & transcripts**: bilingual — Cantonese (colloquial) and English — rather than Putonghua; reflect HK lending products (personal loans, credit-card debt, mortgage arrears) and HK legal-lingo (e.g., "demand letter", "Small Claims Tribunal").
> - **Compliance violations**: use the HK red-line taxonomy from §10.2 (e.g., `third_party_disclosure`, `harassment`, `no_collector_identification`, `misrepresentation`) instead of the generic set.

### 8.1 Demo Requirements

**Objectives**:
- Demonstrate complete workflows from case intake to resolution
- Show GenAI capabilities (summarization, script generation, scoring)
- Illustrate Camunda DMN rule execution and compliance validation
- Display real-time dashboards with meaningful metrics
- Present diverse scenarios (low/medium/high risk, compliant/non-compliant)

**Data Volumes** (Demo Environment):
- 500 cases (various stages of collection)
- 50 collectors (with different performance levels)
- 20 rule sets (assignment, compliance, strategy)
- 2,000 contact history records
- 100 script templates
- 50 compliance violations (for demonstration)

### 8.2 Data Generator Architecture

```
┌──────────────────────────────────────────────────┐
│         Data Generator Service                    │
├──────────────────────────────────────────────────┤
│  Generators:                                      │
│   - CustomerGenerator                             │
│   - CaseGenerator                                 │
│   - ContactHistoryGenerator                       │
│   - RuleGenerator                                 │
│   - ScriptTemplateGenerator                       │
│   - ComplianceViolationGenerator                  │
│   - PerformanceMetricsGenerator                   │
├──────────────────────────────────────────────────┤
│  Templates:                                       │
│   - Chinese names (surnames + given names)        │
│   - Phone numbers (realistic formats)             │
│   - Loan products (消費貸, 信用貸, etc.)          │
│   - Collection scripts (compliant + violations)   │
│   - Case narratives (payment promises, disputes)  │
├──────────────────────────────────────────────────┤
│  Scenarios:                                       │
│   - Early stage delinquency                       │
│   - Long-term overdue                             │
│   - Successful resolution                         │
│   - Escalation to legal                           │
│   - Dispute resolution                            │
└──────────────────────────────────────────────────┘
```

### 8.3 Generator Implementation

**Structure**:
```
data-generator/
├── generators/
│   ├── __init__.py
│   ├── base.py              # Base generator class
│   ├── customers.py         # Customer/borrower data
│   ├── cases.py             # Collection cases
│   ├── contacts.py          # Contact history
│   ├── dmn_rules.py        # Camunda DMN decision-table generator
│   ├── scripts.py           # Script templates
│   └── metrics.py           # Performance metrics
├── templates/
│   ├── chinese_names.json   # Realistic Chinese names
│   ├── addresses.json       # Chinese addresses
│   ├── loan_products.json   # Loan product catalog
│   ├── script_library.json  # Script templates (compliant)
│   ├── violation_examples.json  # Non-compliant scripts
│   └── conversation_flows.json  # Realistic dialogues
├── scenarios/
│   ├── demo_standard.yaml   # Standard demo scenario
│   ├── demo_genai.yaml      # GenAI-focused demo
│   ├── demo_compliance.yaml # Compliance monitoring demo
│   └── demo_executive.yaml  # Executive summary demo
├── utils/
│   ├── faker_chinese.py     # Chinese data faker
│   ├── probability.py       # Weighted random generation
│   └── relationships.py     # Data relationship logic
├── seed_data.py             # Main seeding script
├── config.yaml              # Generation config
└── README.md
```

### 8.4 Generator Components

#### 8.4.1 Customer Generator

```python
# generators/customers.py
from faker import Faker
from typing import Dict, List
import random

class CustomerGenerator:
    def __init__(self, locale='zh_CN'):
        self.faker = Faker(locale)
        self.surnames = self.load_surnames()
        self.given_names = self.load_given_names()
    
    def generate(self, count: int) -> List[Dict]:
        """Generate realistic customer data"""
        customers = []
        
        for _ in range(count):
            customer = {
                "customer_id": f"CUST{self.faker.unique.random_number(digits=10)}",
                "name": self.generate_chinese_name(),
                "id_card": self.generate_id_card(),
                "phone": self.generate_phone(),
                "email": self.faker.email(),
                "address": self.generate_address(),
                "employment_status": random.choice([
                    "employed", "self_employed", "unemployed", "retired"
                ]),
                "monthly_income": random.randint(3000, 50000),
                "credit_score": random.randint(300, 850),
                "customer_segment": self.assign_segment(),
                "registration_date": self.faker.date_between(
                    start_date='-3y',
                    end_date='today'
                ).isoformat()
            }
            customers.append(customer)
        
        return customers
    
    def generate_chinese_name(self) -> str:
        """Generate realistic Chinese name"""
        surname = random.choice(self.surnames)
        given = random.choice(self.given_names)
        return f"{surname}{given}"
    
    def generate_id_card(self) -> str:
        """Generate valid-format Chinese ID card"""
        # Format: 6-digit region + 8-digit birth + 3-digit sequence + 1 check digit
        region = random.choice([
            "110101",  # Beijing
            "310101",  # Shanghai
            "440100",  # Guangdong
            "500000"   # Chongqing
        ])
        birth_date = self.faker.date_of_birth(
            minimum_age=20,
            maximum_age=60
        ).strftime("%Y%m%d")
        sequence = f"{random.randint(1, 999):03d}"
        check_digit = random.randint(0, 9)
        
        return f"{region}{birth_date}{sequence}{check_digit}"
    
    def generate_phone(self) -> str:
        """Generate realistic Chinese mobile number"""
        prefixes = ["130", "131", "132", "133", "135", "136", "137", 
                   "138", "139", "150", "151", "152", "153", "155", 
                   "156", "157", "158", "159", "186", "187", "188", "189"]
        prefix = random.choice(prefixes)
        number = f"{random.randint(0, 99999999):08d}"
        return f"{prefix}{number}"
    
    def generate_address(self) -> str:
        """Generate Chinese address"""
        provinces = ["北京市", "上海市", "廣東省", "浙江省", "江蘇省"]
        cities = {
            "北京市": ["朝陽區", "海淀區", "東城區"],
            "上海市": ["浦東新區", "徐匯區", "黃浦區"],
            "廣東省": ["深圳市", "廣州市", "東莞市"]
        }
        
        province = random.choice(provinces)
        city = random.choice(cities.get(province, ["市區"]))
        street = f"{self.faker.street_name()}街{random.randint(1, 200)}號"
        
        return f"{province}{city}{street}"
    
    def assign_segment(self) -> str:
        """Assign customer segment with weighted probability"""
        return random.choices(
            ["VIP", "premium", "standard", "high_risk"],
            weights=[5, 15, 60, 20]
        )[0]
```

#### 8.4.2 Case Generator

```python
# generators/cases.py
import random
from datetime import datetime, timedelta
from typing import Dict, List

class CaseGenerator:
    def __init__(self, customers: List[Dict]):
        self.customers = customers
        self.loan_products = self.load_loan_products()
    
    def generate(self, count: int) -> List[Dict]:
        """Generate collection cases with realistic scenarios"""
        cases = []
        
        for _ in range(count):
            customer = random.choice(self.customers)
            overdue_days = self.generate_overdue_days()
            
            case = {
                "case_id": f"CASE{random.randint(100000, 999999)}",
                "customer_id": customer["customer_id"],
                "loan_id": f"LOAN{random.randint(100000, 999999)}",
                "loan_product": random.choice(self.loan_products),
                "principal_amount": random.randint(5000, 500000),
                "overdue_amount": self.calculate_overdue_amount(),
                "overdue_days": overdue_days,
                "overdue_date": (
                    datetime.now() - timedelta(days=overdue_days)
                ).isoformat(),
                "status": self.determine_status(overdue_days),
                "priority": self.calculate_priority(overdue_days, customer),
                "assigned_to": None,  # Will be assigned by rules
                "contact_count": random.randint(0, 15),
                "last_contact_date": self.generate_last_contact(),
                "payment_promise": self.generate_payment_promise(),
                "dispute_flag": random.random() < 0.05,  # 5% dispute rate
                "legal_status": self.determine_legal_status(overdue_days),
                "tags": self.generate_tags(overdue_days, customer),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            cases.append(case)
        
        return cases
    
    def generate_overdue_days(self) -> int:
        """Generate overdue days with realistic distribution"""
        # Weighted distribution: more recent cases
        ranges = [
            (1, 30, 40),      # 40% in 1-30 days
            (31, 60, 25),     # 25% in 31-60 days
            (61, 90, 15),     # 15% in 61-90 days
            (91, 180, 12),    # 12% in 91-180 days
            (181, 365, 8)     # 8% in 181-365 days
        ]
        
        range_choice = random.choices(
            ranges,
            weights=[r[2] for r in ranges]
        )[0]
        
        return random.randint(range_choice[0], range_choice[1])
    
    def calculate_overdue_amount(self) -> float:
        """Calculate overdue amount with interest"""
        principal = random.randint(5000, 500000)
        interest_rate = random.uniform(0.05, 0.20)
        return round(principal * (1 + interest_rate), 2)
    
    def determine_status(self, overdue_days: int) -> str:
        """Determine case status based on overdue days"""
        if overdue_days <= 30:
            return random.choice(["new", "in_progress", "contacted"])
        elif overdue_days <= 90:
            return random.choice(["in_progress", "negotiating", "promise_pending"])
        elif overdue_days <= 180:
            return random.choice(["escalated", "legal_review", "negotiating"])
        else:
            return random.choice(["legal_action", "write_off", "settled"])
    
    def calculate_priority(self, overdue_days: int, customer: Dict) -> int:
        """Calculate case priority (1-10)"""
        priority = 5
        
        # Increase priority for longer overdue
        if overdue_days > 90:
            priority += 2
        elif overdue_days > 60:
            priority += 1
        
        # Adjust by customer segment
        if customer["customer_segment"] == "VIP":
            priority += 2
        elif customer["customer_segment"] == "high_risk":
            priority -= 1
        
        return max(1, min(10, priority))
    
    def generate_payment_promise(self) -> Dict:
        """Generate payment promise data"""
        if random.random() < 0.3:  # 30% have promises
            promise_date = datetime.now() + timedelta(days=random.randint(1, 30))
            return {
                "promised_date": promise_date.isoformat(),
                "promised_amount": random.randint(1000, 50000),
                "kept": random.random() < 0.6  # 60% kept promise
            }
        return None
    
    def generate_tags(self, overdue_days: int, customer: Dict) -> List[str]:
        """Generate case tags"""
        tags = []
        
        if overdue_days > 90:
            tags.append("long_term_overdue")
        if customer["customer_segment"] == "VIP":
            tags.append("vip_customer")
        if customer["employment_status"] == "unemployed":
            tags.append("high_risk")
        if random.random() < 0.1:
            tags.append("payment_plan_active")
        if random.random() < 0.05:
            tags.append("lost_contact")
        
        return tags
```

#### 8.4.3 Contact History Generator

```python
# generators/contacts.py
import random
from datetime import datetime, timedelta
from typing import Dict, List

class ContactHistoryGenerator:
    def __init__(self, cases: List[Dict]):
        self.cases = cases
        self.conversation_templates = self.load_conversation_templates()
    
    def generate(self, contacts_per_case: int = 4) -> List[Dict]:
        """Generate contact history for cases"""
        all_contacts = []
        
        for case in self.cases:
            contact_count = min(
                contacts_per_case,
                case.get("contact_count", 0)
            )
            
            for i in range(contact_count):
                contact = self.generate_single_contact(case, i)
                all_contacts.append(contact)
        
        return all_contacts
    
    def generate_single_contact(self, case: Dict, index: int) -> Dict:
        """Generate a single contact record"""
        contact_type = random.choices(
            ["call", "sms", "email", "whatsapp"],
            weights=[60, 25, 10, 5]
        )[0]
        
        days_ago = random.randint(1, case["overdue_days"])
        contact_time = datetime.now() - timedelta(
            days=days_ago,
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59)
        )
        
        # Generate conversation based on contact type
        if contact_type == "call":
            transcript = self.generate_call_transcript(case)
            duration = random.randint(30, 600)  # 30 sec to 10 min
        elif contact_type == "sms":
            transcript = self.generate_sms_content(case)
            duration = None
        else:
            transcript = self.generate_email_content(case)
            duration = None
        
        # Determine outcome
        outcome = self.determine_outcome(contact_type, index, case)
        
        # Analyze sentiment and intent (simulate GenAI output)
        sentiment = self.analyze_sentiment(transcript, outcome)
        intent = self.classify_intent(transcript, outcome)
        
        return {
            "contact_id": f"CONT{random.randint(100000, 999999)}",
            "case_id": case["case_id"],
            "contact_type": contact_type,
            "contact_time": contact_time.isoformat(),
            "duration_seconds": duration,
            "transcript": transcript,
            "sentiment": sentiment,
            "intent": intent,
            "outcome": outcome,
            "created_by": f"collector_{random.randint(1, 50)}",
            "genai_processed": random.random() < 0.8,  # 80% processed by AI
            "compliance_checked": True,
            "compliance_violations": self.check_compliance(transcript)
        }
    
    def generate_call_transcript(self, case: Dict) -> str:
        """Generate realistic call transcript"""
        templates = [
            # Compliant script
            """催收員：您好，我是{bank}貸後服務部的{name}，請問是{customer}先生/女士嗎？
客戶：是的。
催收員：打擾您了。根據我們的記錄，您有一筆消費貸款逾期{days}天，金額為{amount}元。請問您什麼時候方便還款？
客戶：{response}
催收員：好的，我理解您的情況。{followup}
客戶：{final_response}
催收員：感謝您的配合，祝您生活愉快。""",
            
            # Customer objection
            """催收員：您好，這裡是{bank}客服，關於您的貸款逾期事宜...
客戶：我知道了，但是我最近資金週轉有困難。
催收員：我理解您的難處。我們可以協商一個合理的還款計劃，您看下個月能還多少？
客戶：我下個月可能可以還{amount}元。
催收員：好的，我會為您記錄這個承諾。""",
            
            # No answer
            """系統：撥打{phone}...
系統：對方未接聽，已轉語音信箱。
催收員：您好，我是{bank}的{name}，關於您的貸款事宜，請回電{contact_number}。"""
        ]
        
        template = random.choice(templates)
        
        return template.format(
            bank="XX銀行",
            name=f"李{'明' if random.random() < 0.5 else '娟'}",
            customer="張先生",
            days=case["overdue_days"],
            amount=f"{case['overdue_amount']:.0f}",
            phone="13812345678",
            contact_number="400-123-4567",
            response=random.choice([
                "我這個月資金緊張，能不能寬限幾天？",
                "好的，我這兩天就安排還款。",
                "我對這筆貸款有異議，需要核實。"
            ]),
            followup=random.choice([
                "我們可以給您延期到月底。",
                "非常感謝，期待您的還款。",
                "我會為您轉接到爭議處理部門。"
            ]),
            final_response=random.choice([
                "謝謝你的理解。",
                "好的，我會盡快處理。",
                "那我等你們的電話。"
            ])
        )
    
    def generate_sms_content(self, case: Dict) -> str:
        """Generate SMS content"""
        templates = [
            "【XX銀行】尊敬的客戶，您的貸款逾期{days}天，金額{amount}元，請盡快還款。客服電話：400-123-4567",
            "【XX銀行】溫馨提醒：您的還款日期已過期{days}天，請登錄APP或撥打400-123-4567處理。",
            "【XX銀行】您好，您承諾的還款日期已到，請盡快安排還款。如有疑問請聯繫我們。"
        ]
        
        return random.choice(templates).format(
            days=case["overdue_days"],
            amount=f"{case['overdue_amount']:.0f}"
        )
    
    def determine_outcome(
        self,
        contact_type: str,
        index: int,
        case: Dict
    ) -> str:
        """Determine contact outcome"""
        if contact_type == "call":
            outcomes = [
                "payment_promised",
                "payment_arranged",
                "dispute_raised",
                "no_answer",
                "wrong_number",
                "callback_requested",
                "partial_payment_agreed"
            ]
            weights = [20, 15, 5, 30, 5, 15, 10]
        else:
            outcomes = ["delivered", "read", "no_response"]
            weights = [40, 30, 30]
        
        return random.choices(outcomes, weights=weights)[0]
    
    def analyze_sentiment(self, transcript: str, outcome: str) -> str:
        """Simulate GenAI sentiment analysis"""
        if outcome in ["payment_promised", "payment_arranged", "partial_payment_agreed"]:
            return random.choice(["positive", "neutral"])
        elif outcome in ["dispute_raised", "no_answer"]:
            return random.choice(["negative", "neutral"])
        else:
            return "neutral"
    
    def classify_intent(self, transcript: str, outcome: str) -> str:
        """Simulate GenAI intent classification"""
        intent_map = {
            "payment_promised": "willing_to_pay",
            "payment_arranged": "willing_to_pay",
            "dispute_raised": "dispute",
            "no_answer": "unreachable",
            "callback_requested": "need_time",
            "partial_payment_agreed": "negotiating"
        }
        
        return intent_map.get(outcome, "unknown")
    
    def check_compliance(self, transcript: str) -> List[str]:
        """Check for compliance violations"""
        violations = []
        
        # Simulate 5% violation rate for demo
        if random.random() < 0.05:
            violation_types = [
                "threatening_language",
                "harassment",
                "outside_contact_hours",
                "third_party_disclosure",
                "no_collector_identification",
                "misrepresentation"
            ]
            violations.append(random.choice(violation_types))
        
        return violations
```

#### 8.4.4 DMN Decision-Table Generator

```python
# generators/dmn_rules.py
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List

class DMNRuleGenerator:
    """Generate DMN 1.5 decision-table JSON for direct deploy to Camunda 8.
    Produces files matching Camunda's expected DMN model format, so they
    can be uploaded via the Web Modeler or the Camunda 8 Deployments API.
    """

    def __init__(self):
        self.namespace = "https://capco.com/dmn/loan-agent"

    def generate(self) -> Dict[str, dict]:
        return {
            "case_assignment":        self._case_assignment(),
            "case_priority":          self._case_priority(),
            "contact_strategy":       self._contact_strategy(),
            "red_line_compliance":    self._red_line_compliance(),
        }

    # ---------- helpers ----------
    def _wrap(self, decision_id: str, name: str, hit_policy: str,
              inputs: List[dict], outputs: List[dict], rules: List[List[str]],
              citations: List[str]) -> dict:
        return {
            "namespace": self.namespace,
            "id": f"{decision_id}-{uuid.uuid4().hex[:6]}",
            "name": name,
            "hitPolicy": hit_policy,
            "inputs":  inputs,
            "outputs": outputs,
            "rules":   [{"ruleId": f"R{i+1}", "inputs": r[:len(inputs)],
                         "outputs": r[len(inputs):]} for i, r in enumerate(rules)],
            "citations": citations,   # clause references from the HK RAG KB
            "version":  1,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

    # ---------- decision tables ----------
    def _case_assignment(self) -> dict:
        return self._wrap(
            decision_id="case-assignment",
            name="Case assignment (priority queue routing)",
            hit_policy="PRIORITY",
            inputs=[
                {"label": "Customer segment", "expr": "case.customerSegment"},
                {"label": "Overdue days",     "expr": "case.overdueDays"},
                {"label": "Overdue amount",   "expr": "case.overdueAmount"},
            ],
            outputs=[
                {"label": "Assignee skill",      "expr": "result.skill"},
                {"label": "Priority",            "expr": "result.priority"},
                {"label": "Strategy suggestion", "expr": "result.strategy"},
            ],
            rules=[
                ["VIP",    "any",            "any",     "senior",       9, "high_value_negotiation"],
                ["any",    ">180",           ">50000",  "legal_team",  10, "legal_review"],
                ["any",    "31-90",          "any",     "standard",     6, "regular_followup"],
                ["standard","1-30",          "<10000",  "junior",       3, "sms_reminder"],
                ["any",    "1-30",           "<50000",  "junior",       5, "phone_followup"],
                ["standard","1-30",          ">50000",  "standard",     7, "dedicated_handling"],
                ["high_risk",">90",          "<50000",  "agency",       4, "agency_outsource"],
            ],
            citations=[
                "LMLA Code of Practice §5 (Terms and Conditions)",
                "Money Lenders Ordinance Cap.163 s.19",
            ],
        )

    def _red_line_compliance(self) -> dict:
        return self._wrap(
            decision_id="red-line-compliance",
            name="Hong Kong red-line compliance check",
            hit_policy="UNIQUE",
            inputs=[
                {"label": "Contact time (hour)",   "expr": "action.contactHour"},
                {"label": "Contact type",          "expr": "action.contactType"},
                {"label": "Collector identified?", "expr": "action.collectorIdentified"},
                {"label": "Wording analysis",      "expr": "action.wordingClass"},
                {"label": "Third party involved?", "expr": "action.thirdPartyInvolved"},
                {"label": "Debt disclosed to 3rd?", "expr": "action.debtDisclosedTo3rdParty"},
            ],
            outputs=[
                {"label": "Decision",  "expr": "result.decision"},
                {"label": "Violation", "expr": "result.violationType"},
            ],
            rules=[
                ["any", "any", "No",  "any", "any", "any",                            "block", "no_collector_identification"],
                ["<8 or >21", "any", "Yes", "any", "any", "any",                     "block", "outside_contact_hours"],
                ["any", "any", "Yes", "harassment_or_threat", "any", "any",           "block", "harassment"],
                ["any", "any", "Yes", "misrepresentation", "any", "any",              "block", "misrepresentation"],
                ["any", "any", "Yes", "any", "Yes", "Yes",                             "block", "third_party_disclosure"],
                ["any", "third_party", "Yes", "any", "No", "No",                       "allow", "-"],
                ["8-21", "sms/call/email", "Yes", "neutral_or_compliant", "No", "No", "allow", "-"],
            ],
            citations=[
                "LMLA Code of Money Lending Practice §19 (Debt Collection Activities)",
                "LMLA Code of Money Lending Practice §8 (Personal Referees)",
                "Money Lenders Ordinance Cap.163 s.29 (Offences by money lenders)",
                "Code of Banking Practice (HKMA/HKAB) — fair treatment",
            ],
        )

    def _contact_strategy(self) -> dict:
        return self._wrap(
            decision_id="contact-strategy",
            name="Contact channel & time recommendation",
            hit_policy="FIRST",
            inputs=[
                {"label": "Case stage",     "expr": "case.stage"},
                {"label": "Customer persona","expr": "case.persona"},
                {"label": "Historical response", "expr": "case.responseRate"},
            ],
            outputs=[
                {"label": "Channel", "expr": "result.channel"},
                {"label": "Window",  "expr": "result.window"},
                {"label": "Script",  "expr": "result.script"},
            ],
            rules=[
                ["early", "office_worker",    "high", "call", "18:00-20:00", "early_stage_reminder"],
                ["early", "retiree",          "high", "call", "10:00-16:00", "early_stage_reminder"],
                ["early", "any",              "low",  "sms",  "any",         "early_stage_sms"],
                ["mid",   "any",              "any",  "call+sms", "19:00-21:00", "mid_stage_followup"],
                ["late",  "any",              "any",  "call", "working_hours", "late_stage_negotiation"],
            ],
            citations=[
                "LMLA Code of Practice §19 (reasonable hours/frequency)",
            ],
        )

    def _case_priority(self) -> dict:
        return self._wrap(
            decision_id="case-priority",
            name="Initial case priority (worklist ordering)",
            hit_policy="UNIQUE",
            inputs=[
                {"label": "Overdue days",   "expr": "case.overdueDays"},
                {"label": "Overdue amount", "expr": "case.overdueAmount"},
            ],
            outputs=[
                {"label": "Priority", "expr": "result.priority"},
            ],
            rules=[
                ["<=30",  "<10000",  3],
                ["<=30",  "10000-50000", 5],
                ["<=30",  ">50000",   7],
                ["31-90", "any",      6],
                ["91-180","any",      8],
                [">180",  ">50000",  10],
                [">180",  "<50000",   9],
            ],
            citations=["LMLA Code of Practice §5"],
        )
```

Generated DMN JSON is dropped into `camunda-models/dmn/` and deployed via the Camunda 8 Deployments REST API (`POST /api/deployments`).

### 8.5 Demo Scenarios

#### Scenario 1: Standard Demo (30 minutes)
**Purpose**: Show end-to-end workflow

**Data Generated**:
- 200 cases (mix of early/mid/late stage)
- 30 collectors
- 10 rule sets
- 800 contact records

**Demo Flow**:
1. Dashboard overview (metrics, charts)
2. New case intake → Auto-assignment by Camunda DMN
3. GenAI case summarization
4. Collector uses AI script generation
5. Camunda DMN compliance check (block violation)
6. Successful payment promise
7. Analytics dashboard

#### Scenario 2: GenAI-Focused Demo (45 minutes)
**Purpose**: Highlight AI capabilities

**Data Generated**:
- 100 cases with rich contact history
- Multiple conversation transcripts
- Script templates (compliant + violations)
- A/B test results

**Demo Flow**:
1. GenAI case summary generation
2. Natural language rule creation
3. Script generation with compliance check
4. Intent/sentiment analysis on transcripts
5. Quality check automation (100% vs 5% sampling)
6. Strategy recommendation with confidence scores
7. Trust gate demonstration (auto/review/escalate)

#### Scenario 3: Compliance Demo (20 minutes)
**Purpose**: Show compliance monitoring

**Data Generated**:
- 50 compliance violations (various types)
- Real-time violation detection examples
- Audit trail

**Demo Flow**:
1. Real-time violation detection
2. Camunda DMN red-line enforcement
3. Historical violation trends
4. Drill-down by collector/type
5. Compliance dashboard

#### Scenario 4: Executive Demo (15 minutes)
**Purpose**: High-level business value

**Data Generated**:
- Summary metrics only
- ROI comparison data
- Before/after GenAI integration

**Demo Flow**:
1. Key metrics (recovery rate, efficiency, compliance)
2. GenAI vs traditional comparison
3. Cost savings
4. Risk reduction
5. Scalability roadmap

### 8.6 Seeding Script

```python
# seed_data.py
import asyncio
import yaml
from generators import *
from database import get_session
from models import *

async def seed_demo_data(scenario: str = "standard"):
    """Main seeding function"""
    
    # Load scenario config
    with open(f"scenarios/demo_{scenario}.yaml") as f:
        config = yaml.safe_load(f)
    
    print(f"🌱 Seeding demo data for scenario: {scenario}")
    
    # Initialize generators
    customer_gen = CustomerGenerator()
    case_gen = CaseGenerator([])
    contact_gen = ContactHistoryGenerator([])
    rule_gen = DMNRuleGenerator()  # generates DMN JSON deployable to Camunda 8
    script_gen = ScriptTemplateGenerator()
    
    # Generate data
    print("📊 Generating customers...")
    customers = customer_gen.generate(config["customers_count"])
    await bulk_insert(Customer, customers)
    
    print("📋 Generating cases...")
    case_gen.customers = customers
    cases = case_gen.generate(config["cases_count"])
    await bulk_insert(Case, cases)
    
    print("📞 Generating contact history...")
    contact_gen.cases = cases
    contacts = contact_gen.generate(config["contacts_per_case"])
    await bulk_insert(ContactHistory, contacts)
    
    print("⚖️ Generating DMN decision tables...")
    dmn_models = rule_gen.generate()
    await deploy_dmn_to_camunda(dmn_models)  # POST to Camunda 8 /api/deployments
    
    print("📝 Generating script templates...")
    scripts = script_gen.generate(config["script_templates_count"])
    await bulk_insert(ScriptTemplate, scripts)
    
    print("✅ Demo data seeded successfully!")
    print(f"   - {len(customers)} customers")
    print(f"   - {len(cases)} cases")
    print(f"   - {len(contacts)} contacts")
    print(f"   - {len(scripts)} script templates")
    
    # Generate summary statistics for demo
    stats = await generate_demo_stats()
    print("\n📈 Demo Statistics:")
    print(f"   - Average overdue: {stats['avg_overdue_days']} days")
    print(f"   - Total overdue amount: ${stats['total_overdue']:,.0f}")
    print(f"   - Contact success rate: {stats['contact_success_rate']:.1%}")
    print(f"   - Compliance rate: {stats['compliance_rate']:.1%}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario",
        choices=["standard", "genai", "compliance", "executive"],
        default="standard"
    )
    parser.add_argument("--reset", action="store_true", help="Clear existing data")
    
    args = parser.parse_args()
    
    if args.reset:
        print("🗑️  Clearing existing data...")
        # Run database reset
    
    asyncio.run(seed_demo_data(args.scenario))
```

### 8.7 Usage

```bash
# Install dependencies
cd data-generator
uv pip install -e .

# Generate standard demo data
python seed_data.py --scenario standard

# Generate GenAI-focused demo
python seed_data.py --scenario genai

# Reset and regenerate
python seed_data.py --scenario standard --reset

# Quick demo mode (minimal data for fast iteration)
python seed_data.py --scenario standard --quick
```

### 8.8 Demo Checklist

**Before Demo**:
- [ ] Run data generator with appropriate scenario
- [ ] Verify all services are running (`docker-compose up`)
- [ ] Check dashboard displays data correctly
- [ ] Test GenAI endpoints are responsive
- [ ] Prepare demo script with key talking points
- [ ] Have backup screenshots if live demo fails

**During Demo**:
- [ ] Start with dashboard overview
- [ ] Show real-time case assignment
- [ ] Demonstrate GenAI features with live generation
- [ ] Trigger compliance violation example
- [ ] Show analytics and metrics
- [ ] Q&A with prepared answers

**Demo Talking Points**:
- "This case was automatically summarized by GenAI in 2 seconds"
- "The system processes 100% of calls for compliance, not just 5% sampling"
- "Camunda DMN enforces hard compliance rules that GenAI cannot override"
- "Trust gate routes low-confidence decisions to human review"
- "Natural language rule creation reduces rule deployment from days to minutes"

---

## 9. Testing Strategy

### 8.1 Unit Tests

**Backend** (pytest):
```python
# tests/services/test_genai.py
def test_summarize_case(mock_llm):
    service = SummarizerService(llm=mock_llm)
    summary = service.summarize(case_data)
    assert len(summary) < 500
    assert "逾期" in summary
```

**Frontend** (Jest + React Testing Library):
```typescript
// __tests__/components/case-summary.test.tsx
it('displays AI-generated summary', async () => {
  render(<CaseSummary caseId="123" />);
  await waitFor(() => {
    expect(screen.getByText(/逾期30天/)).toBeInTheDocument();
  });
});
```

**Camunda DMN** (modeler-driven, asserted via REST):
```java
@Test
public void testComplianceRedline() {
    ksession.insert(new CallScript("威脅客戶"));
    ksession.fireAllRules();
    assertTrue(complianceViolationDetected);
}
```

### 8.2 Integration Tests

**API Tests** (pytest + httpx):
```python
async def test_genai_to_dmn_flow():
    # Generate script via GenAI
    script = await client.post("/genai/generate-script", json=case)
    
    # Validate via Camunda DMN (Business Rule Task in BPMN)
    compliance = await client.post(
        f"{CAMUNDA_URL}/v1/process-instances",
        json={"processDefinitionId": "compliance-check", "variables": script.json()},
    )
    assert compliance["is_compliant"] == True
```

### 8.3 End-to-End Tests

**Playwright** (frontend flows):
```typescript
test('case assignment workflow', async ({ page }) => {
  await page.goto('/cases/new');
  await page.fill('[name=customer_id]', '12345');
  await page.click('button:has-text("AI建議分案")');
  await expect(page.locator('.assignment-result')).toBeVisible();
});
```

### 8.4 GenAI Quality Tests

**Eval Framework**:
```python
# tests/genai/test_quality.py
def test_summarization_quality():
    """Test summary contains key facts"""
    cases = load_test_cases()
    for case in cases:
        summary = genai_service.summarize(case)
        assert contains_overdue_days(summary, case)
        assert contains_amount(summary, case)
        assert sentiment_appropriate(summary)
```

**Human Eval**:
- Phase 2: 100% human review of GenAI outputs
- Phase 3: 50% spot check
- Phase 4+: 10% audit sampling

---

## 9. Deployment

### 9.1 Local Development

```bash
# Camunda 8 + GenAI
cd camunda-models
docker-compose up -d   # Zeebe + Operate + Tasklist

# Backend
cd ../loan-agent-backend
uv pip install -e .
uvicorn app.main:app --reload --port 8000

# Frontend
cd ../loan-agent-frontend
npm install
npm run dev
```

### 9.2 Production (Kubernetes)

**Architecture**:
```
Ingress (NGINX)
    ├── /api → FastAPI (3 replicas)
    ├── /camunda → Camunda Operate/Tasklist (2 replicas)
    └── / → Next.js (3 replicas)

Services:
- PostgreSQL (StatefulSet)  ← Camunda state + app DB
- Redis (StatefulSet)
- Vector DB (StatefulSet)
- Camunda Zeebe (StatefulSet, 3 brokers)
```

**Helm Charts**:
```yaml
# values.yaml
fastapi:
  replicaCount: 3
  image: registry.capco.com/loan-agent-backend:latest
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: url

camunda:
  replicaCount: 2
  image: registry.capco.com/camunda-platform:latest
  env:
    - name: CAMUNDA_DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: url

nextjs:
  replicaCount: 3
  image: registry.capco.com/loan-agent-frontend:latest
```

### 9.3 CI/CD Pipeline

**GitHub Actions**:
```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv pip install -e ".[dev]"
      - run: pytest
  
  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
  
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [backend-test, frontend-test]
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/
```

---

## 10. Security & Compliance

### 10.1 Data Protection

- **Regulatory basis**: Personal Data (Privacy) Ordinance (Cap. 486 / PDPO), Data Protection Principles (DPP1–6). Collection must be lawful and proportionate; use limited to the stated purpose; data subject access and correction rights; retention limited to what is necessary.

- **PII Handling**:
  - Encrypt at rest (PostgreSQL TDE)
  - Encrypt in transit (TLS 1.3)
  - PII masking in logs
  - RBAC for data access

- **GenAI Data Flow**:
  - Remove PII before sending to external LLM APIs
  - Use Azure OpenAI / private deployments for sensitive data
  - Audit all prompts and responses

### 10.2 Compliance Features

- **Red-line Rules** (enforced by **Camunda 8 DMN decision tables** — non-negotiable, GenAI cannot override; invoked from BPMN Business Rule Tasks; grounded in the Code of Money Lending Practice and Money Lenders Ordinance Cap. 163):
  - **Collector identification** — every outgoing contact must state the collector's name, the money-lender's identity, and the purpose of the contact.
  - **No third-party disclosure** — do not contact or disclose the debt to family, friends, employers, or referees unless that party is legally liable (guarantor) or the contact is for a permitted purpose (e.g., locating the borrower); never reveal debt details.
  - **No harassment / intimidation** — block threatening, abusive, or coercive language; block threats of violence, arrest, or imprisonment.
  - **No misrepresentation** — block any claim to be law enforcement, a court, or a credit-reference agency.
- **Contact time windows** — only reasonable hours (DMN-configurable, default 08:00–21:00).
- **Frequency limits** — reasonable contact frequency (DMN-configurable, default max 3 contact attempts/day).
  - **Prohibited language detection** — profanity, threats, and deceptive phrasing.

- **Audit Trail**:
  - Every action logged with user ID, timestamp
  - GenAI decisions logged with input/output/confidence
  - Immutable audit logs (append-only)

### 10.3 Role-Based Access Control

```python
# Backend RBAC
class Role(enum.Enum):
    COLLECTOR = "collector"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance"

# Permissions
PERMISSIONS = {
    Role.COLLECTOR: ["view_cases", "contact_customer", "use_genai"],
    Role.SUPERVISOR: [..., "reassign_cases", "approve_scripts"],
    Role.ADMIN: [..., "manage_rules", "view_audit"],
    Role.COMPLIANCE_OFFICER: ["view_audit", "view_violations"]
}
```

---

## 11. Monitoring & Observability

### 11.1 Metrics (Prometheus + Grafana)

**Key Metrics**:
- Request latency (p50, p95, p99)
- GenAI API call duration
- Camunda DMN evaluation time
- Trust gate decisions (auto/review/escalate ratio)
- Compliance violation rate
- Case resolution rate

**Dashboards**:
- System health (CPU, memory, DB connections)
- Business metrics (cases processed, calls made, recovery rate)
- GenAI performance (confidence distribution, human review rate)
- Compliance monitoring (violations over time, by type)

### 11.2 Logging (ELK Stack)

```python
# Structured logging
logger.info(
    "genai_request",
    extra={
        "case_id": case_id,
        "service": "summarizer",
        "confidence": 0.87,
        "trust_gate_decision": "auto_execute",
        "user_id": user_id,
    }
)
```

### 11.3 Alerting

- Compliance violation detected → Immediate Slack alert
- GenAI API error rate > 5% → Page on-call
- Camunda DMN evaluation failure → Alert supervisor
- Trust gate escalation spike → Review dashboard

---

## 12. Cost Estimation

### 12.1 Infrastructure (Monthly)

| Component | Resource | Cost (USD) |
|-----------|----------|------------|
| Kubernetes | 3 nodes (8 vCPU each) | $500 |
| PostgreSQL | RDS instance | $200 |
| Redis | ElastiCache | $100 |
| Vector DB | Qdrant Cloud | $150 |
| Load Balancer | - | $50 |
| **Total** | | **$1,000** |

### 12.2 GenAI API (Monthly)

Assumptions:
- 10,000 cases/month
- 3 GenAI calls per case (summary, script, intent)
- Average 2,000 tokens per call

| Provider | Model | Cost |
|----------|-------|------|
| OpenAI | GPT-4o | $600 |
| Anthropic | Claude Sonnet | $450 |
| Local (self-hosted) | Llama 3 70B | GPU: $800 |

**Recommendation**: Start with OpenAI GPT-4o, migrate to Azure OpenAI (private) in Phase 4.

### 12.3 Development Team

| Role | Count | Months | Cost (USD) |
|------|-------|--------|------------|
| Full-stack Developer | 2 | 6 | $120k |
| Backend Developer (Python) | 1 | 6 | $60k |
| GenAI Engineer | 1 | 6 | $70k |
| UI/UX Designer | 1 | 2 | $20k |
| QA Engineer | 1 | 4 | $30k |
| **Total** | | | **$340k** |

---

## 13. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| GenAI hallucination | RAG grounding + trust gate + Camunda DMN validation |
| Compliance breach | Red-line rules in Camunda DMN (non-negotiable) + audit trail |
| Performance bottleneck | Async processing + caching + horizontal scaling |
| Data privacy | PII anonymization + private LLM deployment |
| User resistance | Copilot-first approach (assistive, not replacement) |
| Vendor lock-in (LLM) | Unified client interface + multi-provider support |

---

## 14. Success Criteria

### Phase 1-2 (Assistive)
- [ ] 80% of collectors use GenAI summary feature
- [ ] Script generation adoption > 50%
- [ ] Zero compliance violations from GenAI outputs

### Phase 3 (Rule Generation)
- [ ] Rule creation time reduced by 60%
- [ ] Non-technical staff can create rules
- [ ] Zero rule conflicts in production

### Phase 4 (Decision Support)
- [ ] 30% of cases handled with GenAI strategy
- [ ] A/B test shows ≥10% improvement in recovery rate
- [ ] Trust gate accuracy > 85%

### Phase 5-6 (Automation)
- [ ] 100% call quality check (vs. 5% sampling)
- [ ] 40% of low-risk cases fully automated
- [ ] Compliance violation detection < 1 hour
- [ ] Overall recovery rate improves by 15%

---

## 15. Next Steps

1. **Week 1**: 
   - Finalize technology choices (Camunda vs jBPM, LLM provider)
   - Set up repositories and Docker environment
   - Kickoff meeting with stakeholders

2. **Week 2-3**:
   - Database schema design review
   - API contract definition
   - Begin Phase 0 implementation

3. **Week 4**:
   - Complete Phase 0
   - Demonstrate: All services running, basic auth, health checks
   - Plan Phase 1 sprint

4. **Monthly Reviews**:
   - Demo to business stakeholders
   - Collect feedback on GenAI outputs
   - Adjust priorities based on user adoption

---

## 16. References & Resources

**Documentation**:
- Camunda 8 docs: https://docs.camunda.io/
- Camunda DMN reference: https://docs.camunda.io/docs/components/modeler/dmn/
- pyzeebe (Python worker client): https://github.com/camunda-cloud/zeebe-process-test
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- LangChain: https://python.langchain.com/

**Hong Kong Regulatory References** (also ingested as RAG knowledge base — see §3.5):
- Money Lenders Ordinance (Cap. 163): https://www.elegislation.gov.hk/hk/cap163
- Personal Data (Privacy) Ordinance (Cap. 486 / PDPO): https://www.elegislation.gov.hk/hk/cap486
- PCPD — PDPO overview: https://www.pcpd.org.hk/english/data_privacy_law/ordinance_at_a_Glance/ordinance.html
- Code of Money Lending Practice (LMLA): https://www.lmla.com.hk/ (and Registrar of Money Lenders circulars)
- Guidelines on Licensing Conditions of Money Lenders (Companies Registry): https://www.cr.gov.hk/
- Code of Banking Practice (HKMA/HKAB): https://www.hkma.gov.hk/ and https://www.hkab.org.hk/
- CLIC — Debt Collection: https://www.clic.org.hk/

**Local / Sovereign LLM options for HK** (data residency friendly):
- HKMA GenA.I. Sandbox (with InvestLM): https://www.hkma.gov.hk/
- InvestLM (HKUST — Cantonese/English bilingual finance LLM): https://huggingface.co/investlm

**Sample Code**:
- (To be created in separate repos)

**Decision Log**:
- (Track key architectural decisions in ADR format)

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-02  
**Author**: Technical Planning Team  
**Status**: Draft for Review