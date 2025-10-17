# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from api.routes.query import router as query_router
from api.routes.ingest import router as ingest_router


def create_app() -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="RAG Knowledge Base API",
        description="Advanced RAG system with ACGA capabilities",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(query_router, prefix="/api/v1/query", tags=["query"])
    app.include_router(ingest_router, prefix="/api/v1/ingest", tags=["ingest"])

    @app.get("/")
    async def root():
        return {"message": "RAG Knowledge Base API", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
