from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.init_db import init_db
from app.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="No-Code/Low-Code AI Workflow Builder API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to AI Workflow Builder API",
        "docs": "/docs",
        "health": "/health"
    }
