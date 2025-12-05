# Harvest - Cost & Resource Estimation

This document provides cost estimates for running Harvest in various deployment scenarios.

## Resource Requirements

### Minimum Requirements (Development/Testing)

| Resource | Specification | Notes |
|----------|---------------|-------|
| CPU | 2 cores | For API + Ollama |
| RAM | 4 GB | Llama 3.2 1B requires ~2GB |
| Storage | 10 GB | Model files + logs |
| Network | 1 Mbps | API traffic |

### Recommended Requirements (Production)

| Resource | Specification | Notes |
|----------|---------------|-------|
| CPU | 4+ cores | Better concurrent request handling |
| RAM | 8-16 GB | Larger models, more concurrent requests |
| Storage | 50 GB SSD | Faster model loading |
| GPU (Optional) | 4GB+ VRAM | 10x faster inference |

---

## Deployment Cost Estimates

### Option 1: Local Development (Self-Hosted)

**Cost: $0/month** (excluding electricity)

| Component | Cost |
|-----------|------|
| Ollama | Free (open source) |
| Llama 3.2 Model | Free (open source) |
| FastAPI | Free (open source) |
| Redis | Free (open source) |

**Hardware Power Consumption:**
- Idle: ~50W
- Active inference: ~150-300W (CPU) or ~200-400W (GPU)
- Estimated electricity: $5-15/month depending on usage

---

### Option 2: Cloud VM (AWS EC2)

#### Small Workload (< 1000 requests/day)

| Instance | vCPU | RAM | Cost/Month | Notes |
|----------|------|-----|------------|-------|
| t3.medium | 2 | 4 GB | ~$30 | CPU-only, basic |
| t3.large | 2 | 8 GB | ~$60 | Recommended minimum |
| t3.xlarge | 4 | 16 GB | ~$120 | Better performance |

**Additional Costs:**
| Resource | Cost/Month |
|----------|------------|
| EBS Storage (50GB gp3) | ~$4 |
| Data Transfer (10GB out) | ~$1 |
| **Total (t3.large)** | **~$65/month** |

#### Medium Workload (1000-10000 requests/day)

| Instance | vCPU | RAM | Cost/Month | Notes |
|----------|------|-----|------------|-------|
| c6i.xlarge | 4 | 8 GB | ~$122 | Compute optimized |
| c6i.2xlarge | 8 | 16 GB | ~$244 | High throughput |

**With GPU (for faster inference):**

| Instance | GPU | VRAM | Cost/Month | Notes |
|----------|-----|------|------------|-------|
| g4dn.xlarge | T4 | 16 GB | ~$380 | 5-10x faster inference |
| g5.xlarge | A10G | 24 GB | ~$730 | Best performance |

---

### Option 3: Cloud VM (Google Cloud)

| Machine Type | vCPU | RAM | Cost/Month |
|--------------|------|-----|------------|
| e2-medium | 2 | 4 GB | ~$25 |
| e2-standard-2 | 2 | 8 GB | ~$49 |
| e2-standard-4 | 4 | 16 GB | ~$97 |
| n1-standard-4 + T4 GPU | 4 | 15 GB | ~$350 |

---

### Option 4: Cloud VM (Azure)

| VM Size | vCPU | RAM | Cost/Month |
|---------|------|-----|------------|
| B2s | 2 | 4 GB | ~$30 |
| B2ms | 2 | 8 GB | ~$60 |
| D4s_v3 | 4 | 16 GB | ~$140 |
| NC4as_T4_v3 (T4 GPU) | 4 | 28 GB | ~$380 |

---

### Option 5: Container Services

#### AWS ECS/Fargate

| Configuration | vCPU | RAM | Cost/Month |
|---------------|------|-----|------------|
| Basic | 2 | 4 GB | ~$60 |
| Standard | 4 | 8 GB | ~$120 |

*Note: Fargate doesn't support GPUs. Use ECS on EC2 for GPU workloads.*

#### Google Cloud Run

| Configuration | vCPU | RAM | Cost/1M requests |
|---------------|------|-----|------------------|
| Basic | 2 | 4 GB | ~$50 |
| Standard | 4 | 8 GB | ~$100 |

*Note: Cold starts may impact latency. Not ideal for LLM inference.*

---

### Option 6: Kubernetes (Self-Managed)

**Per Node Cost (AWS EKS):**

| Node Type | vCPU | RAM | Cost/Month |
|-----------|------|-----|------------|
| t3.large | 2 | 8 GB | ~$60 |
| c6i.xlarge | 4 | 8 GB | ~$122 |
| g4dn.xlarge (GPU) | 4 | 16 GB | ~$380 |

**Additional Costs:**
| Resource | Cost/Month |
|----------|------------|
| EKS Control Plane | $72 |
| Load Balancer | ~$16 |
| NAT Gateway | ~$32 |

**Minimum Production Cluster:**
- 2x t3.large nodes: $120
- EKS + networking: $120
- **Total: ~$240/month**

---

## Cost Comparison by Scale

### Requests per Day vs Monthly Cost

| Scale | Requests/Day | Recommended Setup | Est. Cost/Month |
|-------|--------------|-------------------|-----------------|
| Hobby | < 100 | Local machine | $0 |
| Dev/Test | 100-500 | t3.medium | $35 |
| Small | 500-2000 | t3.large | $65 |
| Medium | 2000-5000 | c6i.xlarge | $130 |
| Large | 5000-20000 | c6i.2xlarge + GPU | $600 |
| Enterprise | 20000+ | K8s cluster + GPUs | $2000+ |

---

## Model Size Impact on Resources

| Model | Size | RAM Required | Inference Speed (CPU) | Inference Speed (GPU) |
|-------|------|--------------|----------------------|----------------------|
| llama3.2:1b | 1.3 GB | 2-3 GB | ~5 tokens/sec | ~50 tokens/sec |
| llama3.2:3b | 2.0 GB | 4-5 GB | ~3 tokens/sec | ~40 tokens/sec |
| mistral:7b | 4.1 GB | 8-10 GB | ~1 token/sec | ~30 tokens/sec |
| llama3:8b | 4.7 GB | 10-12 GB | ~0.5 tokens/sec | ~25 tokens/sec |

---

## Cost Optimization Tips

1. **Use Spot/Preemptible Instances**: Save 60-90% on compute
   - AWS Spot: ~$12/month for t3.large
   - GCP Preemptible: ~$15/month for e2-standard-2

2. **Right-size Your Model**: Start with llama3.2:1b, upgrade only if needed

3. **Implement Caching**: Cache common queries to reduce inference calls

4. **Auto-scaling**: Scale down during off-peak hours

5. **Reserved Instances**: 1-year commitment saves 30-40%

6. **Use ARM Instances**: AWS Graviton instances are 20% cheaper
   - t4g.large: ~$48/month vs t3.large: ~$60/month

---

## Sample Monthly Budgets

### Budget: $50/month
- AWS t3.medium or GCP e2-medium
- Llama 3.2 1B model
- ~500 requests/day capacity

### Budget: $150/month
- AWS c6i.xlarge or reserved t3.xlarge
- Llama 3.2 3B model
- ~3000 requests/day capacity

### Budget: $500/month
- AWS g4dn.xlarge (with T4 GPU)
- Mistral 7B or Llama 3 8B model
- ~10000 requests/day capacity
- 10x faster response times

---

## Free Tier Options

| Provider | Free Tier Details |
|----------|-------------------|
| AWS | 750 hours t2.micro/month (12 months) - Too small for LLMs |
| GCP | $300 credit (90 days) - Good for testing |
| Azure | $200 credit (30 days) + 750 hours B1S |
| Oracle Cloud | Always free: 4 ARM cores, 24GB RAM - Great for Ollama! |

**Best Free Option:** Oracle Cloud's always-free ARM instance (4 OCPU, 24GB RAM) can run Ollama with smaller models effectively.

---

## TCO Calculator

```
Monthly Cost = Compute + Storage + Network + Management

Example (Medium workload):
- Compute (c6i.xlarge): $122
- Storage (100GB EBS): $8
- Network (50GB out): $5
- Monitoring (CloudWatch): $5
- Total: ~$140/month
```

---

*Last updated: December 2024*
*Prices are estimates and may vary by region and time*
