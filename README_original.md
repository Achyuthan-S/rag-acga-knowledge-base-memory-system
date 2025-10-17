# README.md

# RAG Knowledge Base 🧠

An advanced Retrieval-Augmented Generation (RAG) system with Adaptive Corrective Graph Augmentation (ACGA) capabilities.

## 🌟 Features

- **Multi-Modal Knowledge Storage**: Vector, Graph, and Structured databases
- **Advanced Memory System**: Working, session, episodic, and semantic memory
- **ACGA Architecture**: Adaptive, Corrective, Graph-Augmented RAG
- **Scalable Design**: From development to production
- **Modern Tech Stack**: FastAPI, Streamlit, ChromaDB, Neo4j, PostgreSQL

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vector Store  │    │   Graph Store   │    │ Structured DB   │
│   (ChromaDB)    │    │    (Neo4j)      │    │ (PostgreSQL)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌─────────────────────────────┴─────────────────────────────┐
    │                Knowledge Base Layer                       │
    └─────────────────────────────┬─────────────────────────────┘
                                 │
    ┌─────────────────────────────┴─────────────────────────────┐
    │            ACGA Processing Engine                         │
    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
    │  │  Adaptive   │ │ Corrective  │ │   Graph Augmented   │ │
    │  │   Routing   │ │     RAG     │ │     Retrieval       │ │
    │  └─────────────┘ └─────────────┘ └─────────────────────┘ │
    └─────────────────────────────┬─────────────────────────────┘
                                 │
    ┌─────────────────────────────┴─────────────────────────────┐
    │               Memory System                               │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
    │  │ Working  │ │ Session  │ │Episodic  │ │   Semantic   │ │
    │  │ Memory   │ │ Memory   │ │ Memory   │ │    Memory    │ │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
    └─────────────────────────────┬─────────────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                API Layer                      │
         │            (FastAPI)                          │
         └───────────────────────┬───────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │               UI Layer                        │
         │            (Streamlit)                        │
         └───────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd rag-knowledge-base

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
# Required: Add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other service API keys
# ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Start Services

```bash
# Start Docker services (Neo4j, PostgreSQL, Redis)
docker-compose up -d

# Wait for services to start (about 30 seconds)
sleep 30

# Initialize databases
python scripts/setup_databases.py
```

### 4. Run the Application

```bash
# Terminal 1: Start FastAPI server
uvicorn api.main:app --reload --port 8000

# Terminal 2: Start Streamlit UI
streamlit run ui/app.py
```

### 5. Access the Application

- **Streamlit UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j/password123)

## 📁 Project Structure

```
rag-knowledge-base/
├── config/                   # Configuration
│   ├── settings.py          # App settings
│   └── prompts.py           # LLM prompts
├── src/                     # Core source code
│   ├── ingestion/           # Document processing
│   ├── knowledge_base/      # Storage layers
│   ├── memory/              # Memory systems
│   ├── retrieval/           # Search strategies
│   ├── acga/                # ACGA components
│   ├── llm/                 # LLM interfaces
│   └── utils/               # Utilities
├── api/                     # FastAPI application
├── ui/                      # Streamlit interface
├── scripts/                 # Setup and utility scripts
└── tests/                   # Test suite
```

## 🔧 Configuration

### Database Services

- **ChromaDB**: Local vector storage (development)
- **Neo4j**: Graph database for relationships
- **PostgreSQL**: Structured data with pgvector
- **Redis**: Caching and session storage

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap | 200 |
| `LLM_MODEL` | OpenAI model | gpt-4o-mini |
| `EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |

## 📊 Usage Examples

### Document Ingestion

```python
# Via API
curl -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document content here", "metadata": {"source": "manual"}}'
```

### Querying

```python
# Via API
curl -X POST "http://localhost:8000/api/v1/query/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "max_results": 5}'
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ingestion.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📈 Monitoring

### Health Checks

- API Health: `GET /health`
- Query Service: `GET /api/v1/query/health`
- Ingestion Stats: `GET /api/v1/ingest/stats`

### Logs

- Application logs: `logs/app.log`
- Docker service logs: `docker-compose logs [service]`

## 🔄 Development Workflow

### Adding New Features

1. **Core Components**: Add to `src/` directory
2. **API Endpoints**: Add to `api/routes/`
3. **UI Components**: Add to `ui/components/`
4. **Tests**: Add to `tests/`
5. **Documentation**: Update README and docstrings

### Code Quality

```bash
# Format code
black src/ api/ ui/
isort src/ api/ ui/

# Lint code
flake8 src/ api/ ui/

# Type checking
mypy src/
```

## 🚀 Production Deployment

### Docker Production Build

```bash
# Build production image
docker build -t rag-knowledge-base:latest .

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Considerations

- Use managed vector databases (Pinecone, Qdrant)
- Set up proper logging and monitoring
- Configure SSL/TLS for external access
- Set up backup strategies for all databases

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) for RAG frameworks
- [ChromaDB](https://www.trychroma.com) for vector storage
- [Neo4j](https://neo4j.com) for graph database
- [FastAPI](https://fastapi.tiangolo.com) for API framework
- [Streamlit](https://streamlit.io) for UI framework

## 📞 Support

For questions and support:
- Create an issue in this repository
- Check the documentation in `docs/`
- Review example implementations in `examples/`

---

**Status**: 🟡 In Development | **Version**: 1.0.0 | **Last Updated**: October 2025