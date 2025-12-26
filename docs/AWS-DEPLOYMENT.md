# Harvest - AWS Deployment Guide

## Overview

This document outlines how to deploy Harvest on AWS, including persistent storage options, compute choices, and a recommended architecture.

---

## Current Storage Architecture

### Where Storage Sits

```
┌─────────────────────────────────────────────────────────────────┐
│                    fastapi_app/services/task_store.py           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────────────────┐   │
│  │  _get_redis()   │────────►│  Redis (Primary Storage)    │   │
│  │                 │         │  - Task state (JSON)        │   │
│  │  Lazy init      │         │  - 7-day TTL per task       │   │
│  │  Connection     │         │  - Sorted set for listing   │   │
│  │  pooling        │         └─────────────────────────────┘   │
│  └────────┬────────┘                     │                     │
│           │                              │ Fallback            │
│           │ On failure                   ▼                     │
│           │                 ┌─────────────────────────────┐    │
│           └────────────────►│  In-Memory Dict (Fallback)  │    │
│                             │  - Same API                 │    │
│                             │  - Lost on restart          │    │
│                             └─────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Client POST /harvest
       │
       ▼
2. create_task() ──► Redis SETEX (7-day TTL)
       │             Redis ZADD (sorted set index)
       │
       ▼
3. Background task runs
       │
       ▼
4. complete_task() ──► Redis GET + UPDATE + SETEX
       │
       ▼
5. Client GET /harvest/{id}
       │
       ▼
6. get_task() ──► Redis GET ──► Deserialize JSON
```

### Redis Key Structure

| Key Pattern | Type | Purpose |
|-------------|------|---------|
| `harvest:task:{uuid}` | String (JSON) | Individual task data |
| `harvest:tasks` | Sorted Set | Task index for listing (score = timestamp) |

---

## AWS Implementation Options

### Option 1: Minimal Setup (Recommended for Start)

**Cost: ~$50-100/month**

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────┐      ┌──────────────────┐               │
│   │   EC2 Instance   │      │  ElastiCache     │               │
│   │   (t3.medium)    │─────►│  Redis           │               │
│   │                  │      │  (cache.t3.micro)│               │
│   │   - Harvest API  │      │                  │               │
│   │   - Ollama       │      │  Persistent      │               │
│   │   - Docker       │      │  storage         │               │
│   └────────┬─────────┘      └──────────────────┘               │
│            │                                                    │
│            │ Port 8000                                          │
│            ▼                                                    │
│   ┌──────────────────┐                                         │
│   │  Application     │                                         │
│   │  Load Balancer   │◄───── HTTPS from Internet               │
│   └──────────────────┘                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**

| Service | Spec | Monthly Cost |
|---------|------|--------------|
| EC2 (t3.medium) | 2 vCPU, 4GB RAM | ~$30 |
| ElastiCache Redis | cache.t3.micro | ~$12 |
| ALB | Application Load Balancer | ~$16 |
| EBS | 50GB gp3 | ~$4 |
| **Total** | | **~$62/month** |

---

### Option 2: Production-Ready (Recommended for Launch)

**Cost: ~$200-400/month**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    VPC (10.0.0.0/16)                     │  │
│   │  ┌─────────────────────────────────────────────────┐    │  │
│   │  │              Public Subnets (2 AZs)              │    │  │
│   │  │  ┌──────────────────────────────────────────┐   │    │  │
│   │  │  │         Application Load Balancer         │   │    │  │
│   │  │  │         (HTTPS termination)               │   │    │  │
│   │  │  └──────────────────────────────────────────┘   │    │  │
│   │  └─────────────────────────────────────────────────┘    │  │
│   │                          │                               │  │
│   │  ┌─────────────────────────────────────────────────┐    │  │
│   │  │              Private Subnets (2 AZs)            │    │  │
│   │  │                                                 │    │  │
│   │  │   ┌─────────────┐       ┌─────────────┐        │    │  │
│   │  │   │   ECS       │       │   ECS       │        │    │  │
│   │  │   │   Task 1    │       │   Task 2    │        │    │  │
│   │  │   │   (API)     │       │   (API)     │        │    │  │
│   │  │   └─────────────┘       └─────────────┘        │    │  │
│   │  │          │                     │                │    │  │
│   │  │          └──────────┬──────────┘                │    │  │
│   │  │                     │                           │    │  │
│   │  │   ┌─────────────────▼─────────────────┐        │    │  │
│   │  │   │      ElastiCache Redis Cluster     │        │    │  │
│   │  │   │      (cache.t3.medium, 2 nodes)    │        │    │  │
│   │  │   └───────────────────────────────────┘        │    │  │
│   │  │                                                 │    │  │
│   │  │   ┌───────────────────────────────────┐        │    │  │
│   │  │   │         EC2 (GPU Instance)         │        │    │  │
│   │  │   │         g4dn.xlarge                │        │    │  │
│   │  │   │         (Ollama + Models)          │        │    │  │
│   │  │   └───────────────────────────────────┘        │    │  │
│   │  └─────────────────────────────────────────────────┘    │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**

| Service | Spec | Monthly Cost |
|---------|------|--------------|
| ECS Fargate | 2 tasks, 0.5 vCPU, 1GB each | ~$30 |
| ElastiCache Redis | cache.t3.medium (2 nodes) | ~$50 |
| EC2 GPU (g4dn.xlarge) | Ollama inference | ~$250 |
| ALB | Application Load Balancer | ~$16 |
| NAT Gateway | Outbound traffic | ~$32 |
| ECR | Container registry | ~$5 |
| **Total** | | **~$383/month** |

---

### Option 3: Serverless (Cost-Optimized)

**Cost: ~$20-100/month (usage-based)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Serverless Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────┐                                         │
│   │   API Gateway    │◄───── HTTPS                             │
│   │   (HTTP API)     │                                         │
│   └────────┬─────────┘                                         │
│            │                                                    │
│            ▼                                                    │
│   ┌──────────────────┐      ┌──────────────────┐               │
│   │   Lambda         │─────►│  ElastiCache     │               │
│   │   (Harvest API)  │      │  Redis Serverless│               │
│   │                  │      │                  │               │
│   │   - Mangum       │      │  Auto-scaling    │               │
│   │     adapter      │      │  Pay-per-use     │               │
│   └────────┬─────────┘      └──────────────────┘               │
│            │                                                    │
│            │ Invoke                                             │
│            ▼                                                    │
│   ┌──────────────────┐                                         │
│   │   EC2 Spot       │                                         │
│   │   (Ollama)       │                                         │
│   │                  │                                         │
│   │   Or: Bedrock    │                                         │
│   │   (managed LLM)  │                                         │
│   └──────────────────┘                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Note:** This option would require using AWS Bedrock instead of Ollama for LLM inference, as Lambda has timeout limits.

---

## Detailed AWS Service Mapping

### Storage: Amazon ElastiCache for Redis

**Why ElastiCache:**
- Managed Redis service (no ops burden)
- Automatic failover with Multi-AZ
- Encryption at rest and in transit
- Compatible with existing Redis code

**Configuration:**

```python
# config.py - AWS ElastiCache connection
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://harvest-redis.xxxxx.use1.cache.amazonaws.com:6379/0"
)
```

**ElastiCache Setup:**

| Setting | Value |
|---------|-------|
| Engine | Redis 7.x |
| Node Type | cache.t3.micro (dev) / cache.t3.medium (prod) |
| Replicas | 0 (dev) / 1 (prod) |
| Multi-AZ | No (dev) / Yes (prod) |
| Encryption | In-transit + At-rest |
| Auth | Redis AUTH token |

**Estimated Cost:**
- cache.t3.micro: ~$12/month
- cache.t3.medium: ~$50/month
- cache.r6g.large (production): ~$150/month

---

### Compute: Options Comparison

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **EC2** | Simple, full control | Manual scaling | $30-400/mo |
| **ECS Fargate** | Managed containers, auto-scaling | No GPU support | $30-100/mo |
| **EKS** | Kubernetes, GPU support | Complex, expensive | $150-500/mo |
| **Lambda** | Pay-per-use, no servers | 15min timeout, cold starts | $5-50/mo |

**Recommendation:**
- Start with EC2 (Option 1)
- Move to ECS Fargate + EC2 GPU (Option 2) for production

---

### LLM Inference: Options

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **EC2 + Ollama** | Full control, any model | GPU costs, maintenance | $250-750/mo |
| **EC2 Spot + Ollama** | 70% cheaper | Interruptions possible | $75-225/mo |
| **AWS Bedrock** | Managed, no GPU needed | Per-token pricing, limited models | $0.01-0.05/1K tokens |
| **SageMaker** | ML-optimized | Complex, expensive | $200-1000/mo |

**Recommendation:**
- Start with EC2 Spot for Ollama (cost-effective)
- Consider Bedrock for production (simpler, reliable)

---

## Quick Start: Minimal AWS Setup

### Step 1: Create ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id harvest-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx
```

### Step 2: Launch EC2 Instance

```bash
# Launch EC2 with Docker
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key \
  --security-group-ids sg-xxxxx \
  --user-data file://userdata.sh
```

**userdata.sh:**
```bash
#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone and run Harvest
cd /opt
git clone https://github.com/IParikh1/Harvest.git
cd Harvest

# Set Redis URL to ElastiCache
export REDIS_URL="redis://harvest-redis.xxxxx.use1.cache.amazonaws.com:6379/0"

docker-compose up -d
```

### Step 3: Configure Security Groups

```bash
# Allow Redis access from EC2
aws ec2 authorize-security-group-ingress \
  --group-id sg-redis \
  --protocol tcp \
  --port 6379 \
  --source-group sg-ec2

# Allow HTTP/HTTPS to EC2
aws ec2 authorize-security-group-ingress \
  --group-id sg-ec2 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

---

## Environment Variables for AWS

```bash
# .env for AWS deployment
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# ElastiCache Redis
REDIS_URL=redis://harvest-redis.xxxxx.cache.amazonaws.com:6379/0
TASK_TTL_SECONDS=604800

# Security
API_KEYS=your-api-key-1,your-api-key-2
RATE_LIMIT=100/minute

# Input limits
MAX_SOURCE_LENGTH=50000
MAX_QUERY_LENGTH=1000
```

---

## Cost Optimization Tips

1. **Use Reserved Instances** - Save 30-40% on EC2/ElastiCache with 1-year commitment
2. **Use Spot Instances** - Save 60-90% on Ollama GPU instance
3. **Right-size Redis** - Start with t3.micro, scale up as needed
4. **Use ElastiCache Serverless** - Pay only for what you use (new option)
5. **Consider Bedrock** - No GPU management, pay per token

---

## Monitoring & Observability

### CloudWatch Metrics

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name harvest-api-errors \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Recommended Alarms

| Metric | Threshold | Action |
|--------|-----------|--------|
| API 5XX errors | > 10/5min | Alert |
| Redis CPU | > 80% | Scale up |
| Redis Memory | > 80% | Scale up |
| EC2 CPU | > 80% | Scale up |

---

## Next Steps

1. **Create AWS Account** (if not already done)
2. **Set up VPC** with public/private subnets
3. **Deploy ElastiCache Redis** (cache.t3.micro)
4. **Launch EC2 instance** with Docker
5. **Configure security groups**
6. **Deploy Harvest** with docker-compose
7. **Set up ALB** with HTTPS
8. **Configure CloudWatch** monitoring

---

## Questions to Consider

Before deploying, decide:

1. **Single region or multi-region?** (affects cost and complexity)
2. **GPU instance or Bedrock?** (affects cost model)
3. **How many concurrent users?** (affects instance sizing)
4. **Data retention requirements?** (affects Redis sizing)
5. **Compliance requirements?** (affects encryption, VPC design)
