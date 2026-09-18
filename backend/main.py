"""
Main FastAPI Application Entrypoint for Darukaa.Earth AI Biodiversity Intelligence System.
Production-ready: reads PORT and ALLOWED_ORIGINS from environment variables.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.api.routes import router as api_router
from backend.services.vector_store import vector_store


# CORS — controlled by ALLOWED_ORIGINS env var in production
# Set ALLOWED_ORIGINS="https://your-app.vercel.app" in Render environment
_raw_origins = settings.ALLOWED_ORIGINS.strip()
if _raw_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup logging."""
    print(f"[{settings.PROJECT_NAME}] v{settings.VERSION} initialized.")
    print(f"[{settings.PROJECT_NAME}] PORT: {settings.PORT}")
    print(f"[{settings.PROJECT_NAME}] DEBUG: {settings.DEBUG}")
    print(f"[{settings.PROJECT_NAME}] Vector Store chunks indexed: {len(vector_store.chunks)}")
    print(f"[{settings.PROJECT_NAME}] Using ChromaDB: {vector_store.use_chroma}")
    print(f"[{settings.PROJECT_NAME}] CORS origins: {allowed_origins}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-powered Biodiversity Intelligence System reasoning across "
        "multi-variable environmental factors with grounded RAG retrieval."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Mount API Router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Serve built frontend if present (Docker/single-server deployment)
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

