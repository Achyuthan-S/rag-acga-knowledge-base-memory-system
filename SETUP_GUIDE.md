# SETUP_GUIDE.md

# RAG Knowledge Base - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. Environment Setup

```bash
# Navigate to project
cd /Users/achyuthansivasankar/PROJECTS/rag-knowledge-base

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spacy model (optional, for advanced NLP)
# python -m spacy download en_core_web_sm
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Start Docker Services

```bash
# Start all database services
docker-compose up -d

# Wait for services to start (30 seconds)
sleep 30

# Check services are running
docker ps
```

### 4. Initialize Databases

```bash
# Create database schemas and tables
python scripts/setup_databases.py
```

### 5. Ingest Sample Data (Optional)

```bash
# Load sample documents for testing
python scripts/ingest_sample_data.py
```

### 6. Start the Application

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Streamlit UI:**
```bash
source venv/bin/activate
streamlit run ui/app.py
```

### 7. Access the Application

- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password123)

---

## 📝 Testing the System

### Test 1: Ingest a Document via API

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial Intelligence is transforming how we work and live.",
    "metadata": {"source": "test_doc", "category": "AI"}
  }'
```

### Test 2: Query the Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/v1/query/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is RAG?",
    "max_results": 5
  }'
```

### Test 3: Check System Stats

```bash
curl "http://localhost:8000/api/v1/ingest/stats"
```

---

## 🏗️ System Architecture

### Components Implemented

✅ **Document Ingestion Pipeline**
- Multi-format document loader (PDF, DOCX, TXT, CSV, XLSX)
- Intelligent document chunking
- Batch embedding generation
- Metadata extraction and storage

✅ **Knowledge Storage**
- Vector Store (ChromaDB) - Semantic search
- Graph Store (Neo4j) - Relationship queries
- Metadata Store (PostgreSQL) - Structured data
- Cache Layer (Redis) - Performance optimization

✅ **Memory System**
- Working Memory - Short-term context
- Session Memory - Conversation tracking

✅ **Retrieval System**
- Vector Retriever - Similarity search
- Graph Retriever - Relationship traversal
- Hybrid Retriever - Combined strategies with auto-routing

✅ **API Layer**
- FastAPI with async support
- Document ingestion endpoints
- Query endpoints with session management
- Health checks and monitoring

✅ **UI Layer**
- Streamlit interface
- Chat interface
- Document upload
- System statistics

---

## 🔧 Configuration

### Key Settings (in .env)

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional - Defaults provided
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_RESULTS=10
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

### Database Ports

- **PostgreSQL**: 5432
- **Neo4j**: 7474 (HTTP), 7687 (Bolt)
- **Redis**: 6379

---

## 📊 Monitoring

### Health Endpoints

- **API Health**: `GET /health`
- **Query Service**: `GET /api/v1/query/health`
- **Ingestion Stats**: `GET /api/v1/ingest/stats`

### Logs

- Application logs: `logs/app_YYYY-MM-DD.log`
- Docker logs: `docker-compose logs [service_name]`

---

## 🧪 Development Workflow

### Adding Documents

**Via API:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ingest/text",
    json={
        "text": "Your document content here",
        "metadata": {"source": "your_source", "type": "text"}
    }
)
```

**Via Python:**
```python
from src.ingestion.processor import IngestionProcessor

processor = IngestionProcessor()
result = processor.process_file("path/to/your/document.pdf")
```

### Querying

**Via API:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query/ask",
    json={
        "question": "Your question here",
        "search_strategy": "auto",  # or "vector_only", "graph_only", "combined"
        "max_results": 10
    }
)
```

**Via Python:**
```python
from src.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()
results = retriever.search("Your query", strategy="auto", top_k=10)
```

---

## 🐛 Troubleshooting

### Issue: Docker services won't start

**Solution:**
```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: Deletes data)
docker-compose down -v

# Restart
docker-compose up -d
```

### Issue: OpenAI API errors

**Solution:**
- Check your API key in `.env`
- Verify API key is active: https://platform.openai.com/api-keys
- Check rate limits and billing

### Issue: Database connection errors

**Solution:**
```bash
# Check if services are running
docker ps

# Check logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis

# Restart specific service
docker-compose restart postgres
```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# If using virtual environment, make sure it's activated
source venv/bin/activate
```

---

## 🎯 Next Steps

### Additional Features to Implement

1. **ACGA (Adaptive Corrective Graph Augmentation)**
   - Query routing logic
   - Self-corrective RAG
   - Graph-augmented generation

2. **Advanced Memory**
   - Episodic memory
   - Semantic memory
   - Long-term memory persistence

3. **Entity Extraction**
   - NER (Named Entity Recognition)
   - Automatic graph population
   - Relationship extraction

4. **Production Features**
   - Authentication & authorization
   - Rate limiting
   - Monitoring & observability
   - Error handling & retry logic

5. **Testing**
   - Unit tests
   - Integration tests
   - Performance benchmarks

---

## 📚 Resources

- **LangChain Docs**: https://python.langchain.com
- **ChromaDB Docs**: https://docs.trychroma.com
- **Neo4j Docs**: https://neo4j.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Streamlit Docs**: https://docs.streamlit.io

---

## 🤝 Support

For issues or questions:
1. Check logs: `logs/app_*.log`
2. Review Docker logs: `docker-compose logs`
3. Check API docs: http://localhost:8000/docs
4. Verify environment variables in `.env`

---

**Status**: ✅ Core System Functional
**Version**: 1.0.0
**Last Updated**: October 2025