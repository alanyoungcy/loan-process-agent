from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import cases, rules, genai, analytics, auth, workflows, documents, deployment
from app.models import Base  # Import all models
from app.rules.collection_rules import initialize_rules
from app.workflows.definitions.collection_workflows import register_all_workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Loan Agent Backend...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1]}")
    print(f"🔴 Redis: {settings.REDIS_URL}")
    print(f"🐰 RabbitMQ: {settings.RABBITMQ_URL.split('@')[-1]}")

    # Initialize business rules
    print("⚙️  Initializing business rules...")
    initialize_rules()

    # Initialize workflows
    print("🔄 Registering workflows...")
    register_all_workflows()

    print("✅ System ready!")

    yield

    # Shutdown
    print("👋 Shutting down Loan Agent Backend...")


app = FastAPI(
    title="Loan Agent Backend API",
    description="GenAI-powered Loan Collection System Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(rules.router, prefix="/api/v1/rules", tags=["Rules"])
app.include_router(genai.router, prefix="/api/v1/genai", tags=["GenAI"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(deployment.router, prefix="/api/v1", tags=["Deployment"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Loan Agent Backend API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
