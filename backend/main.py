"""
Main FastAPI Application Entrypoint for Darukaa.Earth AI Biodiversity Intelligence System.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.api.routes import router as api_router
from backend.services.vector_store import vector_store

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered Biodiversity Intelligence System reasoning across multi-variable environmental factors with grounded RAG retrieval.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    print(f"[{settings.PROJECT_NAME}] Initialized.")
    print(f"[{settings.PROJECT_NAME}] Vector Store chunks indexed: {len(vector_store.chunks)}")
    print(f"[{settings.PROJECT_NAME}] Using ChromaDB: {vector_store.use_chroma}")


# Optional Static file serving if frontend dist exists
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
