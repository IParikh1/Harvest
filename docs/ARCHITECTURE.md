# Harvest - Technical Architecture

## Overview

This document describes the technical architecture of Harvest, including current implementation, design decisions, and future evolution plans.

---

## 1. Current Architecture

### High-Level System Diagram

```
                              Harvest System Architecture

                                    +-----------------+
                                    |   Docker Host   |
                                    +-----------------+
                                            |
            +------------------+------------+------------+------------------+
            |                  |                         |                  |
            v                  v                         v                  v
    +---------------+  +---------------+         +---------------+  +---------------+
    |   Harvest     |  |    Ollama     |         |    Redis      |  |   Celery      |
    |     API       |  |    Server     |         |    Server     |  |   Worker      |
    |   (FastAPI)   |  |  (LLM Host)   |         |   (Future)    |  |  (Optional)   |
    +---------------+  +---------------+         +---------------+  +---------------+
            |                  |                         |                  |
            |    HTTP/REST     |                         |                  |
            +--------+---------+                         +--------+---------+
                     |                                            |
                     v                                            v
            +---------------+                            +---------------+
            |  Llama 3.2    |                            |  Task Queue   |
            |    Model      |                            |   (Celery)    |
            +---------------+                            +---------------+


    Port Mapping:
    - API:    8000 -> 8000
    - Ollama: 11434 -> 11434
    - Redis:  6379 -> 6379
```

### Component Interactions

```
    Request Flow

    [Client] --(1)--> [FastAPI Routes] --(2)--> [Task Store]
                            |                       |
                            | (3) BackgroundTask    |
                            v                       |
                      [LLM Service] <---------------+
                            |                       |
                            | (4) HTTP POST         |
                            v                       |
                      [Ollama API]                  |
                            |                       |
                            | (5) Response          |
                            v                       |
                      [Task Store] --(6)--> [Client polls]


    1. Client POSTs to /harvest with source + query
    2. Route creates task in store (PENDING status)
    3. Background task triggered for LLM processing
    4. LLM Service calls Ollama API
    5. Response received, task updated (COMPLETED/FAILED)
    6. Client polls GET /harvest/{task_id} for result
```

---

## 2. Directory Structure

```
harvest/
├── fastapi_app/                 # Main API application
│   ├── __init__.py
│   ├── main.py                  # FastAPI app initialization, CORS, lifespan
│   ├── api/
│   │   └── routes.py            # HTTP endpoint definitions
│   ├── core/
│   │   └── config.py            # Environment configuration
│   ├── models/
│   │   ├── models.py            # Database models (unused currently)
│   │   └── schemas.py           # Pydantic request/response models
│   ├── services/
│   │   ├── llm_service.py       # Ollama/OpenAI integration
│   │   ├── task_store.py        # Task state management
│   │   └── gpt_service.py       # Additional GPT utilities
│   └── utils/
│       └── helpers.py           # Utility functions
│
├── pipeline/                    # Data processing pipeline (partially used)
│   ├── data_ingestion/
│   │   └── loader.py            # Data loading utilities
│   ├── gpt_processors/
│   │   └── insight_generator.py # Prompt engineering module
│   ├── tasks/
│   │   └── harvest_jobs.py      # Celery task definitions
│   └── vector_db/
│       └── vector_handler.py    # Vector DB utilities (future RAG)
│
├── tests/
│   ├── __init__.py
│   └── test_app.py              # Unit tests (26 test cases)
│
├── scripts/
│   └── harvester.py             # CLI utilities
│
├── docs/                        # Documentation (this PR)
│   ├── ASSESSMENT.md
│   ├── ROADMAP.md
│   └── ARCHITECTURE.md
│
├── docker-compose.yml           # Multi-service orchestration
├── Dockerfile                   # API container definition
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── COSTS.md                     # Infrastructure cost analysis
└── README.md                    # Project documentation
```

---

## 3. Component Details

### 3.1 FastAPI Application (`fastapi_app/main.py`)

**Responsibilities**:
- Application initialization
- CORS middleware configuration
- Lifespan management (startup/shutdown)
- Router registration

**Key Design Decisions**:
- Uses `@asynccontextmanager` for clean startup/shutdown
- Permissive CORS (`allow_origins=["*"]`) - needs tightening for production
- Single router for simplicity

```python
# Current initialization pattern
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered data analysis...",
    lifespan=lifespan
)
```

---

### 3.2 API Routes (`fastapi_app/api/routes.py`)

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/harvest` | Submit data for analysis |
| `GET` | `/harvest/{task_id}` | Retrieve task result |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/health` | Health check |

**Request Processing Pattern**:
```python
@router.post("/harvest")
async def run_harvest(request: HarvestRequest, background_tasks: BackgroundTasks):
    task_id = create_task(request.source, request.query)
    background_tasks.add_task(process_harvest_task, task_id, ...)
    return HarvestResponse(task_id=task_id, status=PENDING, ...)
```

**Design Notes**:
- Uses FastAPI's `BackgroundTasks` for async processing
- Synchronous LLM call in background thread (not async)
- Could benefit from async HTTP client (`httpx`)

---

### 3.3 LLM Service (`fastapi_app/services/llm_service.py`)

**Responsibilities**:
- Abstract LLM provider interface
- Ollama API integration
- OpenAI API integration (fallback)
- Health checking

**Provider Architecture**:
```
                    run_llm(prompt, provider=None)
                              |
                    +---------+---------+
                    |                   |
            provider="ollama"   provider="openai"
                    |                   |
                    v                   v
            run_ollama(prompt)   run_openai(prompt)
                    |                   |
                    v                   v
            Ollama API          OpenAI API
            localhost:11434     api.openai.com
```

**Key Configuration**:
```python
# Environment variables
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
```

**Improvement Opportunities**:
- Use `httpx` for async HTTP calls
- Add retry logic with exponential backoff
- Support streaming responses
- Add model parameter validation

---

### 3.4 Task Store (`fastapi_app/services/task_store.py`)

**Current Implementation**: In-memory dictionary

```python
_task_store: Dict[str, Dict[str, Any]] = {}
```

**Task Lifecycle**:
```
    PENDING  -->  PROCESSING  -->  COMPLETED
                      |
                      +--------->  FAILED
```

**Data Structure**:
```python
{
    "task_id": "uuid-string",
    "status": TaskStatus.PENDING,
    "source": "input data",
    "query": "user question",
    "result": None,  # populated on completion
    "error": None,   # populated on failure
    "created_at": datetime,
    "completed_at": None  # populated on completion/failure
}
```

**Migration to Redis**:
```python
# Proposed Redis implementation
import redis
import json

_redis = redis.from_url(REDIS_URL)

def create_task(source: str, query: str) -> str:
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "status": TaskStatus.PENDING.value,
        "source": source,
        "query": query,
        # ...
    }
    _redis.setex(f"task:{task_id}", 86400 * 7, json.dumps(task_data))
    return task_id
```

---

### 3.5 Pydantic Models (`fastapi_app/models/schemas.py`)

**Request/Response Models**:

```python
class HarvestRequest(BaseModel):
    source: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)

class HarvestResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    source: Optional[str]
    query: Optional[str]
    result: Optional[str]
    error: Optional[str]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]
```

**Enum for Status**:
```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 4. Docker Architecture

### Container Services

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| `api` | Custom (Dockerfile) | FastAPI application | 8000 |
| `ollama` | `ollama/ollama:latest` | LLM inference server | 11434 |
| `ollama-pull` | `ollama/ollama:latest` | Model downloader (one-shot) | - |
| `redis` | `redis:7-alpine` | Task persistence (future) | 6379 |
| `worker` | Custom (Dockerfile) | Celery worker (optional) | - |

### Service Dependencies

```
    ollama-pull  -->  ollama  -->  api
                                    |
                                    v
                                  redis  <--  worker (optional)
```

### Health Checks

All critical services have health checks:

```yaml
# API health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3

# Ollama health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 30s
  timeout: 10s
  retries: 5
```

---

## 5. Data Flow

### Successful Request Flow

```
    1. Client POSTs to /harvest
       {
         "source": "Revenue data...",
         "query": "What is the growth trend?"
       }

    2. API creates task in store
       task_id = "abc-123"
       status = PENDING

    3. Background task starts
       status = PROCESSING

    4. LLM Service builds prompt
       "Analyze the following data...
        Data: Revenue data...
        Query: What is the growth trend?"

    5. Ollama processes prompt
       POST http://ollama:11434/api/generate
       {"model": "llama3.2:1b", "prompt": "...", "stream": false}

    6. Response received
       {"response": "The data shows consistent growth..."}

    7. Task completed
       status = COMPLETED
       result = "The data shows consistent growth..."

    8. Client polls GET /harvest/abc-123
       Returns full task with result
```

### Error Flow

```
    1-4. Same as above...

    5. Ollama fails (timeout, connection error, etc.)
       LLMServiceError raised

    6. Task marked failed
       status = FAILED
       error = "Cannot connect to Ollama..."

    7. Client polls and sees error
       {
         "task_id": "abc-123",
         "status": "failed",
         "error": "Cannot connect to Ollama..."
       }
```

---

## 6. Future Architecture

### Production-Ready Architecture

```
                              Load Balancer (nginx/ALB)
                                       |
                        +------+-------+-------+------+
                        |      |       |       |      |
                        v      v       v       v      v
                    [API-1] [API-2] [API-3] [API-4] [API-5]
                        |      |       |       |      |
                        +------+---+---+-------+------+
                                   |
                    +------+-------+-------+------+
                    |      |               |      |
                    v      v               v      v
               [Redis Cluster]         [Ollama Pool]
               (Task Store)            (GPU Nodes)
                    |
            +-------+-------+
            |       |       |
            v       v       v
        [Worker] [Worker] [Worker]
        (Celery)
```

### Key Changes for Scale

1. **Horizontal API Scaling**: Stateless API behind load balancer
2. **Redis Cluster**: Persistent, distributed task storage
3. **Ollama Pool**: Multiple GPU nodes for inference
4. **Celery Workers**: Distributed task processing
5. **Queue-Based Processing**: Decouple API from inference

---

## 7. Security Considerations

### Current State

| Area | Status | Risk |
|------|--------|------|
| Authentication | None | High |
| Rate Limiting | None | High |
| Input Validation | Basic | Medium |
| HTTPS | Not enforced | Medium |
| CORS | Permissive | Medium |

### Recommended Security Enhancements

1. **API Key Authentication**
   ```python
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key not in valid_keys:
           raise HTTPException(status_code=401)
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_api_key)

   @app.post("/harvest")
   @limiter.limit("100/minute")
   async def run_harvest(...):
   ```

3. **Input Size Limits**
   ```python
   source: str = Field(..., max_length=50000)  # 50KB max
   query: str = Field(..., max_length=1000)
   ```

4. **CORS Tightening**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://app.harvest.io"],
       allow_methods=["GET", "POST"],
   )
   ```

---

## 8. Performance Characteristics

### Current Benchmarks (Estimated)

| Metric | 1B Model | 3B Model |
|--------|----------|----------|
| Cold Start | ~2s | ~5s |
| Inference (100 tokens) | ~3s | ~8s |
| Inference (500 tokens) | ~10s | ~25s |
| Max Concurrent | ~5 | ~2 |
| Memory Usage | ~2GB | ~4GB |

### Optimization Opportunities

1. **Request Batching**: Process multiple queries per LLM call
2. **Response Caching**: Cache identical query results
3. **Model Preloading**: Keep model warm in memory
4. **Async HTTP**: Use `httpx` for non-blocking Ollama calls
5. **Streaming**: Return partial results as they generate

---

## 9. Monitoring & Observability

### Current Capabilities

- Health endpoint: `/health`
- Logging: Python logging with timestamps
- Task status: Queryable via `/tasks`

### Recommended Additions

1. **Prometheus Metrics**
   ```python
   # Request count
   harvest_requests_total{status="success|failure"}

   # Latency histogram
   harvest_request_duration_seconds

   # Active tasks
   harvest_tasks_active{status="pending|processing"}
   ```

2. **Structured Logging**
   ```python
   import structlog

   logger = structlog.get_logger()
   logger.info("task_completed", task_id=task_id, duration_ms=123)
   ```

3. **Tracing**
   - Add OpenTelemetry for distributed tracing
   - Trace from API -> LLM -> Response

---

## 10. Testing Architecture

### Current Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| Health Endpoint | 3 | 100% |
| Harvest Endpoint | 5 | 90% |
| Task Store | 6 | 100% |
| LLM Service | 5 | 60% |
| Tasks Endpoint | 2 | 100% |
| **Total** | **21** | ~80% |

### Test Categories

```
tests/
├── test_app.py          # All current tests
│   ├── TestHealthEndpoint
│   ├── TestHarvestEndpoint
│   ├── TestTaskStore
│   ├── TestLLMService
│   └── TestTasksEndpoint
└── (future)
    ├── test_integration.py   # E2E with real Ollama
    ├── test_performance.py   # Load testing
    └── test_security.py      # Security testing
```

### Running Tests

```bash
# Unit tests (mocked)
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=fastapi_app --cov-report=html
```

---

## 11. Deployment Patterns

### Development

```bash
# Local with Ollama
pip install -r requirements.txt
uvicorn fastapi_app.main:app --reload
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# With Celery worker
docker-compose --profile celery up -d
```

### Kubernetes (Future)

```yaml
# Deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: harvest-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: harvest:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
```

---

## 12. Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | LLM backend (`ollama` or `openai`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.2:1b` | Default model |
| `OPENAI_API_KEY` | (none) | OpenAI API key |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `LOG_LEVEL` | `INFO` | Logging level |

### Docker Compose Overrides

```yaml
# docker-compose.override.yml for local development
services:
  api:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app
```

---

This architecture documentation will be updated as the system evolves. See `ROADMAP.md` for planned changes.
