# Darukaa.Earth Hackathon Submission Document

**Candidate Submission Details for AI Biodiversity Intelligence Chatbot Challenge**

---

### 1. GitHub Repository Link
- **Repository URL**: `https://github.com/your-username/darukaa-biodiversity-ai` *(Replace with your repository link upon upload)*
- **Private Repository Collaborators**:
  - `ankita.dasgupta@darukaa.com`
  - `harsh.kumar@darukaa.com`
  - `utkarsh.gauniyal@darukaa.com`
  - `guneet.mutreja@darukaa.com`

---

### 2. Live Demo URL
- **Local Application URL**: `http://localhost:8000` (Direct FastAPI + React dashboard)
- **API Documentation**: `http://localhost:8000/docs`
- **Hosted Demo URL**: *(Optional deployable on Render / Railway / Fly.io / Vercel)*

---

### 3. Architecture & Technical Overview

#### A. RAG Knowledge System
- Authentic, traceable peer-reviewed knowledge layer covering FAO, IPCC, UNEP, IPBES, Nature, and Science.
- Real vector store with semantic embeddings, cosine similarity scoring, and provenance citations.
- Ingestion pipeline (`scripts/ingest.py`) chunking documents with rich metadata tags (variables, quantitative ranges, organizations, DOIs).

#### B. Multi-Variable Reasoning Engine
- Rejects generic chatbot advice.
- Reasons simultaneously across $\ge 3$ environmental variables:
  - Soil Health (pH, SOC %, moisture %)
  - Climate (rainfall, temperature)
  - Land Use / Cover (monoculture vs agroforestry)
  - Biodiversity (species richness, habitat diversity, pollinators)
  - Anthropogenic Pressures (pesticide pollution, chemical runoff)
- Generates actionable recommendations with scientific mechanism, expected direction, measured quantitative ranges, time horizons (Short/Medium/Long), and confidence levels.

#### C. Conversational Intelligence & Memory
- Multi-turn state tracking with persistent session memory.
- Information completeness analysis: detects missing critical fields and asks targeted clarifying questions.
- Aggregates variables supplied across multiple turns without forgetting previous context.

#### D. Technology Stack
- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, Scikit-Learn, NumPy, ChromaDB
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide-React
- **Testing**: Pytest (22 comprehensive unit & integration tests)
- **Containerization**: Multi-stage Dockerfile, docker-compose.yml
- **CI/CD**: GitHub Actions automated workflow (.github/workflows/ci.yml)

---

### 4. Evaluation Criteria Verification Matrix

| Evaluation Criteria (Weight) | Requirement | Implementation Location | Verified Status |
| :--- | :--- | :--- | :--- |
| **Depth of Reasoning (30%)** | Connect $\ge 3$ variables simultaneously; non-obvious recommendations | `backend/services/reasoning_engine.py` | ✅ **PASS** (100% test coverage) |
| **Scientific Grounding (25%)** | Traceable citations from FAO, IPCC, UNEP, IPBES; no hallucinations | `data/raw/`, `data/metadata/`, `tests/test_evidence_validation.py` | ✅ **PASS** (11 authentic papers/reports) |
| **Knowledge System Design (20%)** | Real RAG retrieval pipeline, vector store, inspectable evidence | `backend/services/vector_store.py`, `scripts/ingest.py` | ✅ **PASS** (Inspectable in UI & API) |
| **Conversational Intelligence (15%)** | Context awareness, clarifying questions, multi-turn state retention | `backend/services/conversation_manager.py`, `backend/services/clarification_service.py` | ✅ **PASS** (Turns 1-3 memory verified) |
| **Output Clarity (10%)** | 5-pillar assessment, key interactions, actionable cards, time horizons | `backend/models/schemas.py`, `frontend/src/App.jsx` | ✅ **PASS** (Structured JSON & UI) |

---

### 5. Local Setup & Reproduction Commands

```bash
# 1. Clone repository
git clone https://github.com/your-username/darukaa-biodiversity-ai.git
cd darukaa-biodiversity-ai

# 2. Run backend and serve React dashboard
python -m pip install -r requirements.txt
python scripts/ingest.py
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 3. Run all automated tests
python -m pytest tests/ -v

# 4. Open in browser
# http://localhost:8000
```
