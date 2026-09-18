# Multi-Stage Dockerfile for Darukaa.Earth AI Biodiversity Intelligence Platform
# Render deployment: uses $PORT env var at runtime

# --- Stage 1: Build React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
# Pass build-time API URL (set in Render env or CI)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# --- Stage 2: Python Backend & Static Serving ---
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, data, and scripts
COPY backend/ ./backend/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ingest knowledge chunks into vector store during build
# This is idempotent: re-generates data/processed/knowledge_chunks.json
# from repo-controlled data/raw/*.json files. Safe for redeploy/restart.
RUN python scripts/ingest.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Use sh -c so $PORT is expanded at runtime from Render's env var
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
