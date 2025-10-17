<div align="center">

  <!-- Suggestion: Create a logo and replace the h1 tag. -->
  <h1>ACGA Knowledge Base</h1>

  <p>
    <strong>The first open-source RAG system with a comprehensive, adaptive memory.</strong>
  </p>
  <p>
    Production-ready, hybrid retrieval, and zero-cost deployment.
  </p>

  <br />

  <!-- Badges -->
  <a href="https://github.com/Achyuthan-S/rag-acga-knowledge-base-memory-system/actions">
    <img src="https://img.shields.io/badge/tests-6/6 passing-brightgreen" alt="Tests">
  </a>
  <a href="#benchmarks">
    <img src="https://img.shields.io/badge/latency-85ms-blue" alt="Performance">
  </a>
  <a href="https://github.com/Achyuthan-S/rag-acga-knowledge-base-memory-system/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  </a>
  <a href="#requirements">
    <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  </a>
    <a href="https://github.com/Achyuthan-S/rag-acga-knowledge-base-memory-system/stargazers">
    <img src="https://img.shields.io/github/stars/Achyuthan-S/rag-acga-knowledge-base-memory-system?style=social" alt="GitHub Stars">
  </a>

</div>

<!-- Suggestion: Create a GIF of the UI in action and add it here.
<p align="center">
  <img src="link_to_your_demo.gif" alt="ACGA Knowledge Base Demo" width="800"/>
</p>
-->

---

ACGA (Adaptive Corrective Graph-Augmented) is an enterprise-grade RAG system designed to address the critical gap in open-source solutions: **long-term memory**. While most RAGs are stateless, ACGA remembers, learns, and adapts.

It combines a hybrid retrieval engine with a multi-layered memory system to provide context-aware, personalized, and accurate answers.

## Key Features

| Feature | Description |
| :--- | :--- |
| **Comprehensive Memory** | Four-layer memory system (Working, Session, Episodic, Semantic) retains context across conversations and users. |
| **Hybrid Retrieval** | Adaptively routes queries across **vector**, **graph**, and **keyword** search for optimal accuracy. |
| **Production Performance** | Achieves **85ms** cold query latency and a **15.5x** speedup with caching, benchmarked for real-world loads. |
| **Zero-Cost Deployment** | Runs entirely on the **Google Gemini free tier** and local databases, making it perfect for developers and startups. |
| **Plug-and-Play** | Easily integrate components like the `MemorySystem` or `HybridRetriever` into your existing RAG pipeline. |
| **All-in-One Stack** | Includes everything from data ingestion to a web UI, fully containerized with Docker for immediate deployment. |


## Quick Start: 30-Second Setup

Get the entire system running with a single command.

```bash
git clone https://github.com/Achyuthan-S/acga-knowledge-base.git && cd acga-knowledge-base && make up
```

Your knowledge base is now live:
- **Web Interface**: [http://localhost:8501](http://localhost:8501)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

<br/>
<details>
<summary><strong>Click for Detailed Local Setup & Configuration</strong></summary>

### 1. Clone & Install
```bash
git clone https://github.com/Achyuthan-S/acga-knowledge-base.git
cd acga-knowledge-base

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Add your Google API key (free at https://makersuite.google.com)
# You can also add this to the .env file directly
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### 3. Start Services & Initialize
```bash
# Start databases (Docker required)
docker-compose up -d

# Wait for services to start and initialize
sleep 30
python scripts/setup_databases.py

# Run tests to verify the installation
python scripts/test_system.py
```

### 4. Run the Application
```bash
# Terminal 1: Start API server
uvicorn api.main:app --reload --port 8000

# Terminal 2: Start web interface
streamlit run ui/app.py
```
</details>

## Use as a Library

Integrate ACGA's powerful components directly into your own RAG projects.

### Install from GitHub
```bash
pip install git+https://github.com/Achyuthan-S/acga-knowledge-base.git
```

### Example: Add Memory to Your RAG Pipeline
```python
from rag_knowledge_base.memory import MemorySystem
from rag_knowledge_base.retrieval import HybridRetriever

# 1. Initialize ACGA components
memory = MemorySystem()
retriever = HybridRetriever()

# 2. Use in your existing RAG function
def enhanced_rag(question: str, user_id: str):
    # Get conversation context from memory
    context = memory.get_working_memory(user_id)
    
    # Enhance the query with relevant history
    enhanced_query = memory.enhance_query_with_context(question, context)
    
    # Use the hybrid retriever for better results
    results = retriever.search(enhanced_query, strategies=['vector', 'graph'])
    
    # Your existing LLM generation logic
    answer = your_llm.generate(question, results)
    
    # Store the new interaction back into memory
    memory.store_interaction(user_id, question, answer, results)
    
    return answer

```

## Architecture

The ACGA system is a modular, multi-layered architecture designed for performance and scalability.

<!-- Suggestion: Create a high-quality diagram (e.g., with Excalidraw or Figma) and replace this. -->
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vector Store  │    │   Graph Store   │    │ Structured DB   │
│   (ChromaDB)    │    │    (Neo4j)      │    │ (PostgreSQL)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │              ACGA Engine                      │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
         │  │  Adaptive   │ │ Corrective  │ │  Graph  │ │
         │  │   Routing   │ │     RAG     │ │Augmented│ │
         │  └─────────────┘ └─────────────┘ └─────────┘ │
         └───────────────────────┬───────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │               Memory System                   │
         │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
         │  │ Working  │ │ Session  │ │   Episodic   │  │
         │  │ Memory   │ │ Memory   │ │   & Semantic │  │
         │  │ (Redis)  │ │ (Redis)  │ │(PostgreSQL) │  │
         │  └──────────┘ └──────────┘ └──────────────┘  │
         └───────────────────────┬───────────────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                API & UI Layers                │
         │          (FastAPI & Streamlit)               │
         └───────────────────────────────────────────────┘
```

## Benchmarks

We conducted extensive benchmarks to ensure production-ready performance.

| Metric | Cold Start | Cached | Improvement |
| :--- | :--- | :--- | :--- |
| **Latency** | 85ms | 5ms | **15.5x faster** |
| **Throughput** | 12 QPS | 200 QPS | **16.7x more** |
| **Retrieval (Hybrid)** | **0.85** P@5 | **0.73** R@10 | **Best overall** |

For a complete analysis, see the [full benchmark report](BENCHMARKS.md).

## Contributing

Contributions are welcome! This project thrives on community support.

<details>
<summary><strong>Click for Contribution Guidelines</strong></summary>

### Development Setup
```bash
# Clone the repo and install dev dependencies
git clone https://github.com/Achyuthan-S/acga-knowledge-base.git
cd acga-knowledge-base
pip install -r requirements-dev.txt

# Install pre-commit hooks for code quality
pre-commit install
```

### How to Contribute
1.  **Fork** the repository.
2.  Create a new feature branch (`git checkout -b feature/your-amazing-feature`).
3.  Add your changes and include tests.
4.  Ensure all tests pass (`pytest tests/ -v`).
5.  Submit a **Pull Request**.

</details>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
This project stands on the shoulders of giants. Our thanks to the teams behind:
- [Google Gemini](https://deepmind.google/technologies/gemini/) for the powerful free-tier LLM.
- [ChromaDB](https://www.trychroma.com/), [Neo4j](https://neo4j.com/), [PostgreSQL](https://www.postgresql.org/), and [Redis](https://redis.io/) for the database technologies.
- [FastAPI](https://fastapi.tiangolo.com/) and [Streamlit](https://streamlit.io/) for the web stack.
- The researchers behind RAG, CRAG, and Graph-RAG for the foundational concepts.

---
<div align="center">
  <strong>Star this repository if you find it helpful!</strong>
</div>