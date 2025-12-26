# Harvest - Development Roadmap

## Overview

This document outlines the blockers, gaps, and prioritized development plan to take Harvest from MVP to a market-ready product aligned with the Go-to-Market strategy defined in `ASSESSMENT.md`.

---

## 1. Critical Blockers (P0)

These issues **must be resolved** before any public launch or production use.

### 1.1 No Persistent Storage

| Attribute | Details |
|-----------|---------|
| **Impact** | All tasks lost on API restart |
| **Current State** | In-memory dict in `task_store.py` |
| **Solution** | Integrate Redis (already in docker-compose) |
| **Effort** | Low (2-4 hours) |
| **Files Affected** | `task_store.py`, `config.py` |

**Implementation Notes**:
- Redis container already exists in `docker-compose.yml`
- Replace `_task_store` dict with Redis operations
- Use `REDIS_URL` from config (already defined)
- Consider TTL for old tasks (e.g., 7 days)

---

### 1.2 No Authentication

| Attribute | Details |
|-----------|---------|
| **Impact** | API completely open to anyone |
| **Current State** | No auth middleware |
| **Solution** | Add API key authentication |
| **Effort** | Medium (4-8 hours) |
| **Files Affected** | New `auth.py`, `routes.py`, `config.py` |

**Implementation Notes**:
- Start with simple API key in header (`X-API-Key`)
- Store valid keys in environment or Redis
- Add middleware to validate on all `/harvest` endpoints
- Keep `/health` endpoint public for monitoring

---

### 1.3 No Rate Limiting

| Attribute | Details |
|-----------|---------|
| **Impact** | Vulnerable to abuse, resource exhaustion |
| **Current State** | Unlimited requests allowed |
| **Solution** | Add rate limiting middleware |
| **Effort** | Low (2-4 hours) |
| **Files Affected** | `main.py`, new rate limit dependency |

**Implementation Notes**:
- Use `slowapi` or `fastapi-limiter`
- Default: 100 requests/minute per API key
- Add headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- Return 429 when exceeded

---

### 1.4 No Input Sanitization

| Attribute | Details |
|-----------|---------|
| **Impact** | Potential prompt injection attacks |
| **Current State** | Raw user input passed to LLM |
| **Solution** | Add input validation and sanitization |
| **Effort** | Medium (4-6 hours) |
| **Files Affected** | `routes.py`, `insight_generator.py` |

**Implementation Notes**:
- Limit `source` field to reasonable size (e.g., 50KB)
- Limit `query` field (e.g., 1000 characters)
- Strip potential injection patterns
- Add system prompt to constrain model behavior

---

## 2. Feature Gaps (P1)

Required for competitive positioning and user adoption.

### 2.1 Request Timeout Handling

| Attribute | Details |
|-----------|---------|
| **Impact** | Long prompts can hang indefinitely |
| **Current State** | 120s timeout in `llm_service.py`, no user feedback |
| **Solution** | Configurable timeouts with proper error handling |
| **Effort** | Low (2-3 hours) |

**Implementation Notes**:
- Add `timeout` parameter to `/harvest` endpoint
- Default to 60s, max 300s
- Return meaningful error on timeout
- Consider streaming for long responses (future)

---

### 2.2 Model Selection

| Attribute | Details |
|-----------|---------|
| **Impact** | Users stuck with default model |
| **Current State** | Single model configured at startup |
| **Solution** | Allow model selection per request |
| **Effort** | Medium (4-6 hours) |

**Implementation Notes**:
- Add `model` field to `HarvestRequest`
- Validate against available models from Ollama
- Add `/models` endpoint to list available options
- Cache model list (refresh every 5 minutes)

---

### 2.3 Structured Output

| Attribute | Details |
|-----------|---------|
| **Impact** | Results are unstructured text only |
| **Current State** | Raw LLM response returned |
| **Solution** | Support JSON output format |
| **Effort** | Medium (6-8 hours) |

**Implementation Notes**:
- Add `output_format` parameter: `text` (default), `json`
- Use JSON mode prompting for structured output
- Parse and validate JSON before returning
- Fall back to text if JSON parsing fails

---

### 2.4 Batch Processing

| Attribute | Details |
|-----------|---------|
| **Impact** | No way to process multiple queries efficiently |
| **Current State** | Single request at a time |
| **Solution** | Add batch endpoint |
| **Effort** | Medium (6-8 hours) |

**Implementation Notes**:
- Add `POST /harvest/batch` endpoint
- Accept array of requests
- Return array of task IDs
- Limit batch size (e.g., 10 requests)

---

### 2.5 Webhook Callbacks

| Attribute | Details |
|-----------|---------|
| **Impact** | Clients must poll for results |
| **Current State** | Polling via `GET /harvest/{id}` |
| **Solution** | Optional webhook on completion |
| **Effort** | Medium (4-6 hours) |

**Implementation Notes**:
- Add `callback_url` to `HarvestRequest`
- POST result to callback URL on completion
- Include HMAC signature for verification
- Retry failed webhooks (3 attempts)

---

## 3. Feature Gaps (P2)

Important for product maturity but not blocking launch.

### 3.1 Request History/Analytics

| Attribute | Details |
|-----------|---------|
| **Impact** | No visibility into usage patterns |
| **Current State** | Tasks list only, no analytics |
| **Solution** | Add usage analytics endpoint |
| **Effort** | Medium (6-8 hours) |

---

### 3.2 Multi-Provider Support

| Attribute | Details |
|-----------|---------|
| **Impact** | Limited to Ollama (OpenAI untested) |
| **Current State** | OpenAI code exists but unused |
| **Solution** | Test and document provider switching |
| **Effort** | Low (3-4 hours) |

---

### 3.3 Response Caching

| Attribute | Details |
|-----------|---------|
| **Impact** | Redundant LLM calls for identical requests |
| **Current State** | No caching |
| **Solution** | Cache responses by hash(source + query) |
| **Effort** | Medium (4-6 hours) |

---

### 3.4 Prometheus Metrics

| Attribute | Details |
|-----------|---------|
| **Impact** | Limited observability |
| **Current State** | Health check only |
| **Solution** | Add /metrics endpoint with Prometheus format |
| **Effort** | Medium (4-6 hours) |

---

### 3.5 OpenAPI Spec Enhancement

| Attribute | Details |
|-----------|---------|
| **Impact** | Auto-generated docs could be better |
| **Current State** | Basic FastAPI auto-docs |
| **Solution** | Add detailed examples, descriptions, tags |
| **Effort** | Low (2-3 hours) |

---

## 4. Technical Debt

### 4.1 Test Coverage Gaps

| Area | Current | Target |
|------|---------|--------|
| API Routes | 90% | 95% |
| LLM Service | 60% | 90% |
| Task Store | 100% | 100% |
| Integration Tests | 0% | 50% |

**Actions**:
- Add integration tests with actual Ollama (CI/CD with Ollama container)
- Add edge case tests (timeout, large inputs, malformed requests)
- Add load tests (benchmark requests/second)

---

### 4.2 Error Message Consistency

**Current**: Mixed error formats across endpoints
**Target**: Standardized error response model

```python
class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None
```

---

### 4.3 Logging Standardization

**Current**: Basic logging with inconsistent format
**Target**: Structured JSON logging with correlation IDs

**Actions**:
- Add request ID to all logs
- Use structured logging library (e.g., `structlog`)
- Add log levels per component via config

---

## 5. Documentation Gaps

| Document | Status | Priority |
|----------|--------|----------|
| API Reference | Partial (auto-docs) | P1 |
| Deployment Guide | Partial (README) | P1 |
| Configuration Reference | Missing | P1 |
| Contributing Guide | Missing | P2 |
| Architecture Docs | This PR | P1 |
| Security Considerations | Missing | P1 |
| Performance Tuning | Missing | P2 |

---

## 6. Implementation Timeline

### Phase 1: Production Hardening (Week 1-2)

| Task | Priority | Est. Effort |
|------|----------|-------------|
| Integrate Redis for task persistence | P0 | 4h |
| Add API key authentication | P0 | 6h |
| Add rate limiting | P0 | 3h |
| Add input validation/sanitization | P0 | 4h |
| Improve error handling | P1 | 3h |
| Add request timeout config | P1 | 2h |

**Deliverable**: Production-ready API with basic security

---

### Phase 2: Feature Enhancement (Week 3-4)

| Task | Priority | Est. Effort |
|------|----------|-------------|
| Add model selection per request | P1 | 5h |
| Add `/models` endpoint | P1 | 2h |
| Add JSON output format | P1 | 6h |
| Add webhook callbacks | P1 | 5h |
| Enhance OpenAPI documentation | P2 | 3h |

**Deliverable**: Feature-complete API for beta launch

---

### Phase 3: Scaling & Observability (Week 5-6)

| Task | Priority | Est. Effort |
|------|----------|-------------|
| Add response caching | P2 | 5h |
| Add Prometheus metrics | P2 | 4h |
| Add batch processing endpoint | P1 | 6h |
| Integration test suite | P1 | 8h |
| Load testing & benchmarks | P2 | 4h |

**Deliverable**: Scalable, observable production system

---

### Phase 4: Cloud Deployment (Week 7-8)

| Task | Priority | Est. Effort |
|------|----------|-------------|
| Kubernetes manifests | P1 | 8h |
| CI/CD pipeline (GitHub Actions) | P1 | 6h |
| Multi-tenant support | P1 | 10h |
| Usage tracking & billing hooks | P1 | 8h |
| Landing page & docs site | P1 | 8h |

**Deliverable**: Harvest Cloud beta launch ready

---

## 7. Success Metrics

### Technical KPIs

| Metric | Target |
|--------|--------|
| API Uptime | 99.9% |
| P95 Latency (1B model) | < 5 seconds |
| P95 Latency (3B model) | < 15 seconds |
| Test Coverage | > 80% |
| Error Rate | < 1% |

### Business KPIs (Post-Launch)

| Metric | Month 1 | Month 3 | Month 6 |
|--------|---------|---------|---------|
| Registered Users | 100 | 500 | 2000 |
| Monthly Active Users | 50 | 200 | 800 |
| API Requests/Month | 10K | 100K | 500K |
| Paid Conversions | 5 | 25 | 100 |
| MRR | $150 | $750 | $3000 |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ollama API changes | Medium | High | Pin Ollama version, abstract interface |
| GPU cost scaling | High | Medium | Offer CPU-only tier, optimize prompts |
| Competitor launches similar product | Medium | Medium | Move fast, build community |
| Security vulnerability discovered | Low | High | Regular audits, bug bounty program |
| LLM output quality issues | Medium | Medium | Allow model selection, improve prompts |

---

## 9. Dependencies

### External Dependencies

| Dependency | Risk | Mitigation |
|------------|------|------------|
| Ollama | Medium | Open source, can fork if needed |
| Llama 3.2 | Low | Multiple model options |
| Docker | Low | Industry standard |
| Redis | Low | Multiple alternatives (Valkey, KeyDB) |

### Internal Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Cloud infrastructure | TBD | Not started |
| Billing system | TBD | Not started |
| Marketing site | TBD | Not started |

---

## 10. Next Actions

1. **Immediate**: Review and approve this roadmap
2. **This Week**: Start Phase 1 (production hardening)
3. **Next Week**: Complete P0 blockers
4. **2 Weeks**: Beta launch preparation

See `ARCHITECTURE.md` for technical implementation details.
