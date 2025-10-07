#!/bin/bash
# scripts/start_services.sh

echo "🚀 Starting RAG Knowledge Base Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Docker services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check Neo4j
if curl -f http://localhost:7474 > /dev/null 2>&1; then
    echo "✅ Neo4j is running"
else
    echo "❌ Neo4j is not responding"
fi

# Check PostgreSQL
if docker exec rag-postgres pg_isready -U rag_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is not responding"
fi

# Check Redis
if docker exec rag-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not responding"
fi

echo ""
echo "🎉 Services started! You can now:"
echo "   • Initialize databases: python scripts/setup_databases.py"
echo "   • Start API server: uvicorn api.main:app --reload --port 8000"
echo "   • Start UI: streamlit run ui/app.py"
echo ""
echo "🌐 Service URLs:"
echo "   • Neo4j Browser: http://localhost:7474 (neo4j/password123)"
echo "   • API Docs: http://localhost:8000/docs (when running)"
echo "   • Streamlit UI: http://localhost:8501 (when running)"