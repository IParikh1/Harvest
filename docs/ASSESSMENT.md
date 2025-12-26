# Harvest - Strategic Assessment

## Executive Summary

**Harvest** is a FastAPI-based data analysis tool that uses local LLMs (Ollama with Llama 3.2) to extract insights from unstructured data. It provides a privacy-focused alternative to cloud-based AI services by running entirely on local infrastructure.

| Attribute | Value |
|-----------|-------|
| **Category** | AI-Powered Data Analysis API |
| **Tech Stack** | Python, FastAPI, Ollama, Docker |
| **LLM** | Llama 3.2 (1B/3B) via Ollama |
| **Stage** | MVP Complete |
| **Deployment** | Docker Compose ready |

---

## 1. Assessment of Intent

### Primary Intent

Harvest aims to be a **privacy-first AI data analysis service** that enables:

1. **Local LLM Processing**: All data stays on-premises - no data sent to external APIs
2. **Simple Query Interface**: Submit data + question, receive AI-generated insights
3. **Async Processing**: Background task execution with status tracking
4. **Developer-Friendly**: RESTful API, Docker deployment, extensible architecture

### Target Use Cases

Based on the README examples:
- **Financial Analysis**: Revenue trends, financial health assessments
- **Log Analysis**: Error pattern detection, root cause analysis
- **Document Summarization**: Key point extraction from long documents
- **General Data Insights**: Any unstructured text analysis

### Implied Target Users

| Segment | Characteristics |
|---------|-----------------|
| **Enterprise IT Teams** | Need AI analysis without cloud data exposure |
| **Compliance-Heavy Industries** | Finance, healthcare, legal - data sovereignty requirements |
| **Developers** | Building AI-powered features into existing applications |
| **Privacy Advocates** | Organizations/individuals avoiding cloud AI services |

### Current State of Intent Realization

| Goal | Status | Notes |
|------|--------|-------|
| Local LLM Processing | Complete | Ollama integration working |
| Privacy-First | Complete | No external API calls required |
| RESTful API | Complete | Clean FastAPI implementation |
| Docker Deployment | Complete | Full docker-compose setup |
| Async Processing | Complete | Background tasks with status tracking |
| Production Persistence | Partial | In-memory store (Redis placeholder exists) |
| Multiple LLM Providers | Partial | OpenAI fallback exists but untested |

---

## 2. Assessment of Design

### Architecture Overview

```
                                   Harvest Architecture

    Client                         API Layer                    Processing Layer

    [HTTP Client]  ─────────────►  [FastAPI App]  ─────────────►  [LLM Service]
         │                              │                              │
         │  POST /harvest               │  Background Task             │  Ollama API
         │  GET /harvest/{id}           │  Task Store                  │  (llama3.2:1b)
         │  GET /tasks                  │                              │
         ▼                              ▼                              ▼
    Response JSON               [Task Store (In-Memory)]        [Ollama Container]
                                       │
                                       │ (Future: Redis)
                                       ▼
                               [Celery Worker] (Optional)
```

### Component Breakdown

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `main.py` | `fastapi_app/` | Application entry, CORS, lifespan |
| `routes.py` | `fastapi_app/api/` | HTTP endpoints, request handling |
| `schemas.py` | `fastapi_app/models/` | Pydantic models, validation |
| `config.py` | `fastapi_app/core/` | Environment configuration |
| `llm_service.py` | `fastapi_app/services/` | Ollama/OpenAI integration |
| `task_store.py` | `fastapi_app/services/` | Task state management |
| `insight_generator.py` | `pipeline/gpt_processors/` | Prompt engineering |
| `docker-compose.yml` | Root | Full deployment configuration |

### Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Web Framework** | FastAPI 0.104+ | Async support, auto-docs, Pydantic integration |
| **Validation** | Pydantic 2.5+ | Type-safe request/response models |
| **LLM Runtime** | Ollama | Local LLM inference, no API keys needed |
| **LLM Model** | Llama 3.2 (1B) | Fast inference, low resource requirements |
| **Containerization** | Docker Compose | Multi-service orchestration |
| **Future Queue** | Redis + Celery | Scaffolded but not active |

### Code Quality Assessment

#### Strengths

1. **Clean Architecture**: Clear separation between API, services, and models
2. **Type Safety**: Full Pydantic models for all data structures
3. **Error Handling**: Custom exceptions, proper HTTP status codes
4. **Testing**: 26 test cases covering all major functionality
5. **Docker Ready**: Production-grade docker-compose with health checks
6. **Documentation**: Comprehensive README with examples
7. **Logging**: Structured logging throughout
8. **Extensibility**: OpenAI fallback shows provider-agnostic design

#### Weaknesses

1. **In-Memory Storage**: Tasks lost on restart (Redis not integrated)
2. **No Authentication**: API is completely open
3. **Single Model**: No model switching without restart
4. **No Rate Limiting**: Vulnerable to abuse
5. **Blocking Inference**: Long prompts could timeout
6. **No Retry Logic**: Failed LLM calls not retried
7. **Limited Prompt Engineering**: Basic prompt template

### Design Patterns Used

| Pattern | Implementation |
|---------|----------------|
| **Repository** | `task_store.py` abstracts storage |
| **Factory** | `run_llm()` selects provider dynamically |
| **Background Task** | FastAPI BackgroundTasks for async processing |
| **Health Check** | Dedicated endpoint for monitoring |

---

## 3. Go-to-Market Strategy Analysis

### Market Landscape

#### The AI Data Analysis Market

The market for AI-powered data analysis is experiencing rapid growth:
- **Enterprise AI spending**: $150B+ annually (2024)
- **Privacy concerns**: Growing regulatory pressure (GDPR, CCPA, AI Act)
- **Local-first movement**: Increasing demand for on-prem AI solutions

#### Competitive Landscape

| Category | Competitors | Harvest Differentiation |
|----------|-------------|------------------------|
| **Cloud AI APIs** | OpenAI, Anthropic, Google | Privacy: No data leaves your infrastructure |
| **Enterprise AI Platforms** | Palantir, Databricks AI | Simplicity: Deploy in minutes, not months |
| **Local LLM Tools** | LM Studio, Ollama CLI | API-First: Build into existing applications |
| **RAG Solutions** | LangChain, LlamaIndex | Focused: Simple query interface, no complexity |

### GTM Strategy Options

#### Option A: Open Source + Cloud Service (Recommended)

**Model**: Open-core with managed service

**Strategy**:
1. Keep core Harvest open source (current state)
2. Launch **Harvest Cloud**: Managed Ollama + Harvest API
3. Target: Developers who want privacy but don't want to manage infrastructure

**Pricing**:
| Tier | Price | Included |
|------|-------|----------|
| Free | $0 | 100 requests/month, 1B model |
| Pro | $29/month | 10,000 requests, 3B model, priority support |
| Team | $99/month | 50,000 requests, custom models, SSO |
| Enterprise | Custom | Dedicated instance, SLA, on-prem option |

**Pros**:
- Builds community around open source
- Multiple revenue streams
- Network effects from adoption

**Cons**:
- Requires cloud infrastructure investment
- Support burden
- Competition from larger players

**Revenue Potential**: $50K-500K/year (Year 1-2)

---

#### Option B: Enterprise License Model

**Model**: Self-hosted with paid support

**Strategy**:
1. Release Harvest under dual license (MIT for personal, paid for commercial)
2. Sell annual licenses with support
3. Target: Enterprises with strict data governance

**Pricing**:
| Tier | Price | Included |
|------|-------|----------|
| Startup | $2,500/year | Up to 10 users, email support |
| Business | $10,000/year | Up to 100 users, priority support |
| Enterprise | $50,000+/year | Unlimited, dedicated support, custom features |

**Pros**:
- Higher per-customer revenue
- Clearer enterprise sales motion
- No infrastructure costs

**Cons**:
- Longer sales cycles
- Limited market reach
- Requires sales team

**Revenue Potential**: $100K-1M/year (with sales effort)

---

#### Option C: API Credits Model

**Model**: Pay-per-use API service

**Strategy**:
1. Host Harvest as a metered API
2. Charge per request or token
3. Target: Developers integrating AI into apps

**Pricing**:
| Tier | Cost |
|------|------|
| Llama 3.2 1B | $0.001/request |
| Llama 3.2 3B | $0.003/request |
| Mistral 7B | $0.01/request |
| Custom Models | Contact us |

**Pros**:
- Aligns cost with usage
- Low barrier to entry
- Predictable unit economics

**Cons**:
- Price competition from larger providers
- Need significant scale for profitability
- GPU infrastructure costs

**Revenue Potential**: $20K-200K/year (usage dependent)

---

#### Option D: Consulting/Integration Model

**Model**: Services-led with product

**Strategy**:
1. Use Harvest as demonstration of capability
2. Sell custom AI integration projects
3. Target: Mid-market companies needing AI solutions

**Pricing**:
| Service | Price |
|---------|-------|
| Implementation | $10K-50K |
| Custom Development | $150-300/hour |
| Ongoing Support | $2K-10K/month |

**Pros**:
- Immediate revenue potential
- Deep customer relationships
- High margins

**Cons**:
- Doesn't scale
- Service business limitations
- Distracts from product

**Revenue Potential**: $100K-500K/year

---

### Recommended GTM Strategy

**Primary: Option A (Open Source + Cloud Service)**

**Rationale**:
1. **Market Timing**: Privacy-focused AI is trending
2. **Technical Fit**: Codebase is already Docker-ready for cloud deployment
3. **Community Building**: Open source creates advocates and contributors
4. **Multiple Paths**: Can add enterprise licenses later if demand exists
5. **Low Initial Investment**: Can start with single cloud instance

**Execution Phases**:

| Phase | Timeline | Actions |
|-------|----------|---------|
| **1. Foundation** | Month 1-2 | Fix blockers, add auth, persistent storage |
| **2. Launch** | Month 3 | ProductHunt launch, HackerNews post, Dev.to articles |
| **3. Cloud Beta** | Month 4-5 | Deploy Harvest Cloud, free tier |
| **4. Monetize** | Month 6+ | Launch paid tiers, iterate on pricing |

---

## 4. Pivot Analysis: Stay or Shift?

### Current Direction Score

| Factor | Score (1-10) | Notes |
|--------|--------------|-------|
| Market Opportunity | 8 | Strong demand for private AI |
| Technical Foundation | 7 | Solid MVP, needs hardening |
| Competitive Position | 6 | Differentiated but small |
| Resource Requirements | 5 | Moderate - needs some investment |
| Revenue Potential | 7 | Good if executed well |
| **Total** | **33/50** | |

### Alternative: RAG-as-a-Service Pivot

| Factor | Score (1-10) | Notes |
|--------|--------------|-------|
| Market Opportunity | 9 | RAG is highly demanded |
| Technical Foundation | 4 | Would require significant new development |
| Competitive Position | 4 | LangChain, LlamaIndex dominate |
| Resource Requirements | 3 | High - vector DB, embeddings, etc. |
| Revenue Potential | 7 | Comparable to current path |
| **Total** | **27/50** | |

### Alternative: Data Extraction API Pivot

| Factor | Score (1-10) | Notes |
|--------|--------------|-------|
| Market Opportunity | 7 | Solid B2B demand |
| Technical Foundation | 5 | Some relevant code exists |
| Competitive Position | 5 | Textract, DocuSign, etc. |
| Resource Requirements | 4 | Medium-high |
| Revenue Potential | 6 | Moderate |
| **Total** | **27/50** | |

### Recommendation: **Stay the Course**

The current direction (privacy-first AI data analysis) scores highest. The codebase is well-aligned with this vision, and the market opportunity is real. A pivot would require significant rework with uncertain benefits.

---

## 5. Summary

### Key Takeaways

1. **Harvest is well-positioned** in the privacy-first AI analysis space
2. **MVP is solid** but needs production hardening (auth, persistence)
3. **Recommended GTM**: Open source + managed cloud service
4. **Don't pivot** - current direction has best risk/reward ratio
5. **Immediate priority**: Fix blockers, then launch

### Next Steps

See `ROADMAP.md` for detailed implementation priorities.
