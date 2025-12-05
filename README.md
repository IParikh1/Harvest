# Harvest

A FastAPI-based data analysis tool powered by local LLMs (Ollama) for extracting insights from unstructured data.

## Features

- **LLM-Powered Analysis**: Uses Ollama with Llama 3.2 for local, private data processing
- **Async Task Processing**: Background task execution with status tracking
- **RESTful API**: Clean FastAPI endpoints for data submission and retrieval
- **Docker Ready**: Full containerization with Docker Compose
- **Extensible**: Modular architecture for adding new processors

## Architecture

```
harvest/
├── fastapi_app/
│   ├── api/
│   │   └── routes.py       # API endpoints
│   ├── core/
│   │   └── config.py       # Configuration settings
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── services/
│   │   ├── llm_service.py  # Ollama integration
│   │   └── task_store.py   # Task management
│   └── main.py             # Application entry point
├── pipeline/
│   └── gpt_processors/
│       └── insight_generator.py  # LLM processing logic
├── tests/
│   └── test_app.py         # Unit tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/IParikh1/Harvest.git
cd Harvest

# Start all services (API + Ollama)
docker-compose up -d

# Wait for Ollama to download the model (first run only)
docker-compose logs -f ollama-pull

# API is available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2:1b

# Install Python dependencies
pip install -r requirements.txt

# Run the API
uvicorn fastapi_app.main:app --reload
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "model": "llama3.2:1b"
}
```

### Submit Data for Analysis
```bash
curl -X POST http://localhost:8000/harvest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "Q4 Revenue: $10M, Q3: $8M, Q2: $7M, Q1: $5M",
    "query": "What is the revenue growth trend?"
  }'
```

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "processing",
  "message": "Task submitted successfully"
}
```

### Get Task Result
```bash
curl http://localhost:8000/harvest/{task_id}
```

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "result": "The revenue shows consistent quarterly growth...",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

### List All Tasks
```bash
curl http://localhost:8000/tasks
```

## Configuration

Environment variables for customization:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM backend (ollama) | ollama |
| `OLLAMA_BASE_URL` | Ollama API URL | http://localhost:11434 |
| `OLLAMA_MODEL` | Model to use | llama3.2:1b |
| `LOG_LEVEL` | Logging level | INFO |

### Using Different Models

```bash
# Use a larger model for better accuracy
export OLLAMA_MODEL=llama3.2:3b
ollama pull llama3.2:3b

# Or use Mistral
export OLLAMA_MODEL=mistral:7b
ollama pull mistral:7b
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=fastapi_app
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Start with Celery worker (for background tasks)
docker-compose --profile celery up -d
```

## Example Use Cases

### Financial Analysis
```json
{
  "source": "Annual Report 2024: Revenue $50M (up 25%), Operating costs $30M, Net profit $15M, Employee count increased from 100 to 150.",
  "query": "Summarize the company's financial health and growth trajectory."
}
```

### Log Analysis
```json
{
  "source": "[ERROR] 2024-01-15 Connection timeout to database\n[WARN] 2024-01-15 High memory usage detected\n[ERROR] 2024-01-15 Failed to process request",
  "query": "What are the main issues and their potential causes?"
}
```

### Document Summarization
```json
{
  "source": "<long document text>",
  "query": "Provide a concise summary of the key points."
}
```

## API Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Task accepted (processing) |
| 400 | Bad request (invalid input) |
| 404 | Task not found |
| 500 | Internal server error |

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

### Model Not Found
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3.2:1b
```

### Docker Issues
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs api --tail=100
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with FastAPI
- Powered by Ollama and Llama 3.2
- Script developed with Claude CLI
