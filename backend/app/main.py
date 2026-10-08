import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.claims import router as claims_router
from backend.app.api.v1.copilot import router as copilot_router
from backend.app.api.v1.fraud import router as fraud_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.knowledge import router as knowledge_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.simulator import router as simulator_router
from backend.app.api.v1.ws import router as ws_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("InsuranceClaimAgent")

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multimodal Insurance Claim Triage AI Agent API",
    description="Enterprise multi-agent system for automated multimodal insurance claim triage, fraud detection, and explainable decision support.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for serving damage photos and annotated images
uploads_dir = os.path.abspath(settings.STORAGE_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include API v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(claims_router, prefix="/api/v1")
app.include_router(copilot_router, prefix="/api/v1")
app.include_router(fraud_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(simulator_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Multimodal Insurance Claim Triage Agent",
        "llm_provider": settings.LLM_PROVIDER,
        "database": "connected"
    }

@app.get("/")
def root():
    return {
        "name": "Multimodal Insurance Claim Triage AI Agent Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Run seed data automatically on startup if database is empty
@app.on_event("startup")
def startup_seed():
    try:
        from backend.seed_data import seed_database
        seed_database()
    except Exception as e:
        logger.warning(f"Startup seeding notice: {e}")
