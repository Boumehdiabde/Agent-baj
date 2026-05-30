# 🚀 Agent BAJ - Quick Start Guide

## Overview
Agent BAJ is a multi-agent AI system powered by FastAPI, supporting OpenAI, Anthropic, and Google's LLM models. It features task routing, caching, and database persistence.

## Prerequisites
- Docker & Docker Compose installed
- Python 3.10+ (for local development)
- Valid API keys for at least one LLM provider

## 🐳 Quick Start with Docker (Recommended)

### 1. Clone & Setup
```bash
git clone https://github.com/Boumehdiabde/Agent-baj.git
cd Agent-baj
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Pick at least ONE LLM provider
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
# OR
GOOGLE_API_KEY=AIza...
```

### 3. Start Services
```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ FastAPI App (port 8000)

### 4. Verify Installation
```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f app

# Health check
curl http://localhost:8000/health
```

### 5. Access API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 💻 Local Development Setup

### 1. Create Virtual Environment
```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure (PostgreSQL & Redis Only)
```bash
docker-compose up -d postgres redis
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and local DB connection
```

### 5. Run FastAPI
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 API Endpoints

### Request Task
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research Python async/await patterns",
    "agent_type": "research",
    "llm_provider": "openai"
  }'
```

### Agent Types
- **research**: Gathers and analyzes information
- **coding**: Generates and debugs code
- **writing**: Creates and edits content
- **analysis**: Performs data analysis

### LLM Providers
- `openai` - GPT-4, GPT-3.5-turbo
- `anthropic` - Claude 2, Claude Instant
- `google` - PaLM 2

---

## 🔧 Configuration

### Environment Variables
```env
# FastAPI
FASTAPI_ENV=development|production
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true|false

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
SQLALCHEMY_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
API_KEY=your-api-key

# Agent Settings
MAX_ITERATIONS=10
TIMEOUT=300

# LLM Providers (pick at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

---

## 🛑 Common Issues & Solutions

### Issue: "Connection refused" to PostgreSQL
```bash
# Ensure postgres service is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Issue: Redis connection error
```bash
# Test redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Issue: API not responding
```bash
# Check app logs
docker-compose logs app

# Ensure app is running
docker-compose restart app

# Verify port 8000 is available
lsof -i :8000
```

### Issue: "ModuleNotFoundError" locally
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🧪 Testing

### Run Tests
```bash
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Manual API Testing
```bash
# Simple health check
curl http://localhost:8000/health

# Test with research agent
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is machine learning?",
    "agent_type": "research",
    "llm_provider": "openai"
  }'
```

---

## 📦 Project Structure
```
Agent-baj/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container setup
├── docker-compose.yml     # Multi-service orchestration
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── agents/               # Agent implementations
├── core/                 # Core modules (llm, router, security)
└── tests/                # Test suite
```

---

## 🚀 Deployment

### Using Docker
```bash
# Build production image
docker build -t agent-baj:latest .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENAI_API_KEY=sk-... \
  agent-baj:latest
```

### Using Docker Compose (Production)
```bash
# Update docker-compose.yml for production
# Set FASTAPI_ENV=production
# Set real SECRET_KEY and API_KEY
# Use production database connection

docker-compose -f docker-compose.yml up -d
```

---

## 🤝 Contributing
1. Create a feature branch
2. Make changes
3. Run tests: `pytest`
4. Submit PR

## 📄 License
MIT License - See LICENSE file

## 🆘 Support
For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API logs: `docker-compose logs app`

---

**Happy coding! 🎉**
