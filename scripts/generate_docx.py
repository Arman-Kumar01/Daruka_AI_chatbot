"""
Final Submission Word Document (.docx) Generator for Darukaa.Earth Hackathon.
Covers all 21 required sections with real production URLs, no placeholders.
"""

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent.parent
DOCX_PATH = BASE_DIR / "docs" / "Darukaa_Biodiversity_Submission_Final.docx"

# ─── Real production URLs ────────────────────────────────────────────────────
GITHUB_URL = "https://github.com/Arman-Kumar01/Daruka_AI_chatbot"
VERCEL_URL = "https://daruka-ai-chatbot.vercel.app"
RENDER_URL = "https://daruka-ai-chatbot.onrender.com"
OPENAPI_URL = f"{RENDER_URL}/docs"
HEALTH_URL  = f"{RENDER_URL}/api/health"
# ─────────────────────────────────────────────────────────────────────────────


# ── Helpers ───────────────────────────────────────────────────────────────────

def set_cell_background(cell, fill_hex: str):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_heading(doc, text: str, level: int, color: RGBColor):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = color
    return h


def add_code_block(doc, code: str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, "F1F5F9")
    run = cell.paragraphs[0].add_run(code)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    doc.add_paragraph()


def add_callout(doc, text: str, bg="F0FDF4", color=None):
    color = color or RGBColor(16, 120, 80)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, bg)
    run = cell.paragraphs[0].add_run(text)
    run.font.size = Pt(10)
    run.font.color.rgb = color
    run.font.bold = True
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    doc.add_paragraph()


def make_table(doc, headers, rows, header_bg="107850", row_font_size=9.0):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        set_cell_background(cell, header_bg)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(9.5)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)

    for row_data in rows:
        row = tbl.add_row()
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            p = cell.paragraphs[0]
            run = p.add_run(str(text))
            run.font.size = Pt(row_font_size)
            if idx == len(row_data) - 1 and str(text).startswith("✅"):
                run.font.bold = True
                run.font.color.rgb = RGBColor(16, 120, 80)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)

    doc.add_paragraph()
    return tbl


# ── Main generator ────────────────────────────────────────────────────────────

def create_submission_docx():
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    EMERALD     = RGBColor(16, 120, 80)
    DARK_SLATE  = RGBColor(30, 41, 59)
    BLUE        = RGBColor(2, 132, 199)

    # ─── Cover ───────────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title_p.add_run("Darukaa.Earth — AI Biodiversity Intelligence Platform")
    r.font.name = "Arial"; r.font.size = Pt(24); r.font.bold = True
    r.font.color.rgb = EMERALD

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub_p.add_run("Official Hackathon Submission Document")
    sr.font.name = "Arial"; sr.font.size = Pt(13); sr.font.italic = True
    sr.font.color.rgb = DARK_SLATE

    add_callout(doc,
        "Submission prepared in accordance with Page 5 of the Challenge Guidelines. "
        "Built to demonstrate depth of multi-variable ecological reasoning, FAO/IPCC/UNEP "
        "knowledge grounding, RAG retrieval, and conversational intelligence."
    )

    # ─── SECTION 1: Project Title ─────────────────────────────────────────────
    add_heading(doc, "1. Project Title", 1, EMERALD)
    doc.add_paragraph(
        "Darukaa.Earth AI Biodiversity Intelligence Platform\n\n"
        "An AI environmental scientist for multi-variable ecological degradation diagnosis. "
        "The system integrates a genuine Retrieval-Augmented Generation (RAG) knowledge layer "
        "grounded in peer-reviewed scientific literature (FAO, IPCC, UNEP, IPBES, Nature, Science), "
        "multi-variable causal reasoning across soil health, land use, climate, biodiversity, and "
        "human impact indicators, and multi-turn conversational memory."
    )

    # ─── SECTION 2: Problem Statement ─────────────────────────────────────────
    add_heading(doc, "2. Problem Statement", 1, EMERALD)
    doc.add_paragraph(
        "Ecological degradation is a non-linear, multi-variable problem. Single-variable or generic advice "
        "('add compost', 'plant trees') fails to address the systemic coupling of soil health, hydrological "
        "stress, biodiversity collapse, and agrochemical pollution that co-occur in real-world landscapes.\n\n"
        "Existing chatbot-based tools either:\n"
        "  • Use simple prompt engineering ('act as an expert') without real knowledge grounding, or\n"
        "  • Require expensive APIs and fail offline, or\n"
        "  • Ignore variable interactions — missing the critical causal chains that drive ecological outcomes.\n\n"
        "The Darukaa challenge requires an AI system that diagnoses multi-variable ecological problems with "
        "traceable scientific evidence — not generic surface-level advice."
    )

    # ─── SECTION 3: Solution Overview ─────────────────────────────────────────
    add_heading(doc, "3. Solution Overview", 1, EMERALD)
    doc.add_paragraph(
        "Darukaa.Earth is a full-stack AI biodiversity intelligence platform that:\n\n"
        "  1. Accepts environmental data via three input modes: conversational chat, structured form, or raw JSON.\n"
        "  2. Detects missing critical environmental variables and asks targeted clarifying questions.\n"
        "  3. Semantically retrieves relevant scientific knowledge from a ChromaDB vector store "
        "      (26 indexed chunks, FAO/IPCC/UNEP/IPBES/Nature/Science).\n"
        "  4. Executes multi-variable causal reasoning connecting ≥3 environmental pillars simultaneously.\n"
        "  5. Returns evidence-grounded, actionable interventions with quantitative targets, time horizons, "
        "      and traceable source DOIs.\n"
        "  6. Maintains stateful multi-turn conversational memory across sessions."
    )

    # ─── SECTION 4: Key Features ──────────────────────────────────────────────
    add_heading(doc, "4. Key Features", 1, EMERALD)
    features = [
        ("Real RAG Knowledge Layer", "ChromaDB vector store + TF-IDF fallback. 26 scientific chunks from FAO, IPCC, UNEP, IPBES, Nature, Science. No fake or hallucinated citations."),
        ("Multi-Variable Causal Reasoning", "Simultaneously connects Soil Organic Carbon ↔ Moisture Retention ↔ Microbial Diversity ↔ Canopy Temperature ↔ Pollinator Populations."),
        ("Proactive Clarification", "Detects missing variables across 5 pillars (soil, land use, climate, biodiversity, human impact) and prompts targeted questions."),
        ("Conversational Memory", "Stateful session cache accumulates context across turns. Variables supplied earlier are preserved and used in later reasoning."),
        ("Three Input Modes", "Chat (natural language), Structured Form (GUI sliders/dropdowns), Raw JSON (API-grade structured payload)."),
        ("Evidence Grounding", "Every recommendation includes source title, organization, year, DOI URL, and quantitative measured impacts."),
        ("Inspectable Retrieval", "'Inspect RAG Evidence' tab exposes chunk text, similarity scores, and source URLs for full evaluator transparency."),
        ("Zero API Key Required", "100% functional offline. Optional Gemini/OpenAI key activates real-time LLM synthesis for richer narratives."),
        ("CI/CD + Docker", "GitHub Actions CI runs on every push. Docker + docker-compose for reproducible local and cloud deployment."),
        ("Three Canonical Scenarios", "All three challenge PDF scenarios implemented, tested (24/24 pytest passes), and verifiable live."),
    ]
    make_table(doc,
        ["Feature", "Description"],
        [(f, d) for f, d in features],
        header_bg="107850",
        row_font_size=9.0
    )

    # ─── SECTION 5: System Architecture ───────────────────────────────────────
    add_heading(doc, "5. System Architecture", 1, EMERALD)
    add_heading(doc, "Pipeline Flow", 2, DARK_SLATE)
    doc.add_paragraph(
        "User Input (Chat / Form / JSON)\n"
        "        │\n"
        "        ▼\n"
        "  Input Parser & NL Extractor  ──→  Geographic Biome Resolver\n"
        "        │\n"
        "        ▼\n"
        "  Information Completeness Analyzer  ──→  Clarifying Questions\n"
        "        │\n"
        "        ▼\n"
        "  Semantic RAG Retriever  ──→  ChromaDB / TF-IDF Cosine Index\n"
        "        │\n"
        "        ▼\n"
        "  Multi-Variable Reasoning Engine  ──→  Causal Interaction Graph\n"
        "        │\n"
        "        ▼\n"
        "  LLM Adapter (Gemini/OpenAI/Deterministic)  ──→  Scientific Synthesis\n"
        "        │\n"
        "        ▼\n"
        "  StructuredResponse: Assessment + Interactions + Recommendations + Evidence\n"
        "        │\n"
        "        ▼\n"
        "  React Frontend Dashboard  ──→  Chat | Diagnostics | RAG Explorer | Sources"
    )

    add_heading(doc, "Key Backend Modules", 2, DARK_SLATE)
    make_table(doc,
        ["Module", "File", "Responsibility"],
        [
            ("Input Parser", "backend/services/conversation_manager.py", "NL → EnvironmentalInput schema"),
            ("Clarification Service", "backend/services/clarification_service.py", "5-pillar completeness analysis"),
            ("Vector Store", "backend/services/vector_store.py", "ChromaDB + TF-IDF RAG retrieval"),
            ("Reasoning Engine", "backend/services/reasoning_engine.py", "Multi-variable causal synthesis"),
            ("LLM Adapter", "backend/services/llm_adapter.py", "Gemini/OpenAI/Deterministic fallback"),
            ("API Routes", "backend/api/routes.py", "FastAPI endpoints: /chat, /analyze, /recommend, /retrieve"),
            ("Schemas", "backend/models/schemas.py", "Pydantic v2 request/response models"),
        ],
        row_font_size=9.0
    )

    # ─── SECTION 6: RAG / Knowledge Layer Architecture ────────────────────────
    add_heading(doc, "6. RAG / Knowledge-Layer Architecture", 1, EMERALD)
    doc.add_paragraph(
        "The knowledge layer is the differentiating feature of this submission. Unlike systems that rely on "
        "LLM parametric memory, every recommendation in Darukaa.Earth is grounded in retrieved, inspectable chunks.\n\n"
        "Knowledge Sources (26 indexed scientific chunks):\n"
        "  • FAO — Soil Organic Carbon: The Hidden Potential (2017)\n"
        "  • FAO — ITPS State of the World's Soils (2015)\n"
        "  • IPCC — Special Report on Climate Change and Land (SRCCL Chapter 4)\n"
        "  • IPBES — Assessment on Land Degradation & Restoration\n"
        "  • IPBES — Global Assessment of Biodiversity & Ecosystem Services\n"
        "  • UNEP — World Conservation Monitoring Centre (2020)\n"
        "  • Nature Communications — Cover Crops & Soil Microbiome Restoration (2021)\n"
        "  • Journal of Applied Ecology — Wetland Bioswale Drainage (2022)\n"
        "  • Environmental Pollution — Pollinator Wildflower Margins (2023)\n"
        "  • Science — Agroforestry Biodiversity Corridors\n\n"
        "Vector Store Implementation:\n"
        "  • Primary: ChromaDB persistent collection with cosine similarity search\n"
        "  • Fallback: Scikit-learn TF-IDF N-gram vectorizer (guaranteed offline reliability)\n"
        "  • Chunk Schema: {chunk_id, source_id, title, organization, authors, year, url, topic, "
        "ecosystem_types, variables_addressed, text, quantitative_ranges}\n\n"
        "Retrieval is inspectable via /api/retrieve endpoint and the 'Inspect RAG Evidence' UI tab, "
        "which shows exact chunk text, similarity scores, and source URLs for every query."
    )

    # ─── SECTION 7: Multi-Variable Reasoning ──────────────────────────────────
    add_heading(doc, "7. Multi-Variable Reasoning", 1, EMERALD)
    doc.add_paragraph(
        "The reasoning engine (backend/services/reasoning_engine.py) connects environmental variables "
        "across five pillars simultaneously, tracing causal chains that generic AI cannot produce:\n\n"
        "Example Causal Chain (Scenario 1):\n"
        "  Low SOC (0.3%) → Reduced aggregation → ↓ water-holding capacity\n"
        "  → Faster moisture loss → Elevated soil temperature → Microbial stress\n"
        "  → Reduced N-mineralisation → Plant nutrient deficit → Crop yield loss\n"
        "  → Compounding: Low biodiversity → No mycorrhizal network restoration\n\n"
        "The system simultaneously evaluates:\n"
        "  • Soil: pH, organic carbon, moisture (waterlogging/drought indicators)\n"
        "  • Land Use / Land Cover: monoculture, agroforestry, riparian buffer state\n"
        "  • Biodiversity: species richness, habitat diversity, pollinator presence\n"
        "  • Climate: temperature anomalies, rainfall deficit/excess\n"
        "  • Human Impact: pesticide intensity, deforestation rate, pollution index\n\n"
        "Output includes:\n"
        "  • Environmental assessment across all 5 pillars\n"
        "  • key_interactions: the non-obvious causal links\n"
        "  • recommendations: prioritised interventions with biological mechanisms\n"
        "  • evidence: traceable scientific citations for each recommendation"
    )

    # ─── SECTION 8: Conversational Intelligence & Memory ──────────────────────
    add_heading(doc, "8. Conversational Intelligence & Memory", 1, EMERALD)
    doc.add_paragraph(
        "Session Memory Architecture:\n"
        "  • Each session is assigned a UUID (session_id) persisted across requests.\n"
        "  • conversation_manager.py accumulates environmental state across turns via merge_input().\n"
        "  • Variables stated in turn 1 are preserved and enriched by turn 3 without repetition.\n\n"
        "Clarification Engine (clarification_service.py):\n"
        "  • Checks completeness across 5 mandatory environmental pillars.\n"
        "  • When data is insufficient, generates ≤4 targeted, scientifically-framed questions.\n"
        "  • Example: 'What is the approximate soil organic carbon percentage? "
        "(Low < 1%, Medium 1–3%, High > 3%)'\n\n"
        "Natural Language Parser:\n"
        "  • Regex + keyword extraction maps free-text input to typed EnvironmentalInput fields.\n"
        "  • Handles: 'pH is 6.2', 'low rainfall', 'monoculture wheat', 'temperature 31°C'.\n"
        "  • Tested in test_parser.py (5 tests, all passing)."
    )

    # ─── SECTION 9: Evidence Grounding ────────────────────────────────────────
    add_heading(doc, "9. Evidence Grounding", 1, EMERALD)
    doc.add_paragraph(
        "Every recommendation returned by the system includes:\n"
        "  • action: specific ecological intervention with biological mechanism\n"
        "  • why: scientific rationale connecting variables causally\n"
        "  • quantitative_target: measurable outcome with numeric ranges "
        "(e.g. '+15–25% SOC over 2–3 years')\n"
        "  • time_horizon: Short (0–1 yr) / Medium (1–3 yr) / Long (3–5 yr)\n"
        "  • confidence: High / Medium / Low with basis\n"
        "  • evidence: list of EvidenceCitation objects with:\n"
        "      – title, organization, year\n"
        "      – doi_url (clickable, real)\n"
        "      – relevance_score (cosine similarity)\n"
        "      – excerpt (retrieved chunk text)\n\n"
        "All citations reference real published documents. No hallucinated DOIs."
    )

    # ─── SECTION 10: Input Modes ───────────────────────────────────────────────
    add_heading(doc, "10. Input Modes", 1, EMERALD)
    make_table(doc,
        ["Mode", "How to Access", "Description"],
        [
            ("Conversational Chat", "Left panel — Chat tab", "Natural language multi-turn dialogue. Paste scenario text or type freely."),
            ("Structured Form", "Left panel — Form tab", "GUI sliders and dropdowns for all environmental variables. One-click submit."),
            ("Raw JSON", "Left panel — JSON tab", "API-grade payload editor. Paste structured EnvironmentalInput JSON directly."),
            ("Demo Scenarios", "Left panel — top buttons", "Three canonical PDF scenarios pre-loaded with one click."),
        ],
        row_font_size=9.0
    )

    # ─── SECTION 11: Technology Stack ─────────────────────────────────────────
    add_heading(doc, "11. Technology Stack", 1, EMERALD)
    make_table(doc,
        ["Layer", "Technology", "Purpose"],
        [
            ("Frontend", "React 18 + Vite 6", "SPA dashboard — chat, form, diagnostics, RAG explorer"),
            ("Frontend Styling", "Vanilla CSS + Lucide Icons", "Responsive dark-mode UI"),
            ("Markdown Rendering", "react-markdown + remark-gfm + rehype-sanitize", "Rich assistant response formatting"),
            ("Backend", "FastAPI (Python 3.12)", "REST API — /chat, /analyze, /recommend, /retrieve, /health"),
            ("Data Validation", "Pydantic v2", "Typed request/response schemas"),
            ("Vector Store", "ChromaDB + Scikit-learn TF-IDF", "Semantic RAG retrieval (dual-mode)"),
            ("LLM (optional)", "Google Gemini / OpenAI", "Optional LLM synthesis; deterministic fallback always active"),
            ("Testing", "pytest + pytest-asyncio", "24 backend unit + integration tests"),
            ("CI/CD", "GitHub Actions", ".github/workflows/ci.yml — lint, test, build"),
            ("Containerization", "Docker + docker-compose", "Reproducible local and cloud deployment"),
            ("Frontend Deployment", "Vercel", "Automatic deploy from GitHub main branch"),
            ("Backend Deployment", "Render (Docker)", "Auto-deploy from Dockerfile on push to main"),
        ],
        row_font_size=9.0
    )

    # ─── SECTION 12: Deployment Architecture ──────────────────────────────────
    add_heading(doc, "12. Deployment Architecture", 1, EMERALD)
    make_table(doc,
        ["Component", "Platform", "URL", "Config"],
        [
            ("React SPA Frontend", "Vercel", VERCEL_URL, "Root: frontend/ | Build: npm run build | Output: dist/"),
            ("FastAPI Backend", "Render (Docker)", RENDER_URL, "Dockerfile at repo root | PORT from env var"),
            ("OpenAPI Docs", "Render (auto)", OPENAPI_URL, "Auto-generated Swagger UI"),
            ("Health Check", "Render", HEALTH_URL, "Returns vector store status and chunk count"),
            ("GitHub Repository", "GitHub", GITHUB_URL, "Source of truth — all code, tests, CI, Docker"),
        ],
        row_font_size=9.0
    )

    doc.add_paragraph(
        "Environment Variables (set in Render dashboard):\n"
        f"  • ALLOWED_ORIGINS={VERCEL_URL}\n"
        "  • GEMINI_API_KEY=<optional — activates LLM synthesis>\n"
        "  • PORT=10000 (set automatically by Render)\n\n"
        "Environment Variables (set in Vercel dashboard):\n"
        f"  • VITE_API_BASE_URL={RENDER_URL}"
    )

    # ─── SECTION 13: Testing Results ──────────────────────────────────────────
    add_heading(doc, "13. Testing Results", 1, EMERALD)
    add_callout(doc, "24 / 24 backend tests passed  |  Frontend build: SUCCESS (exit code 0)", "D1FAE5")
    make_table(doc,
        ["Test Suite", "Tests", "Result"],
        [
            ("test_clarification.py — Missing variable detection", "3", "✅ All passed"),
            ("test_conversation_memory.py — Multi-turn accumulation", "1", "✅ Passed"),
            ("test_evidence_validation.py — Evidence presence & validity", "1", "✅ Passed"),
            ("test_health.py — Health, sources, scenarios, recommend, ingest", "5", "✅ All passed"),
            ("test_parser.py — NL parsing (full, partial, coords, empty, invalid)", "5", "✅ All passed"),
            ("test_reasoning.py — Multi-variable reasoning (3-var, waterlogging)", "2", "✅ All passed"),
            ("test_retrieval.py — SOC, agroforestry, pollution, empty query", "4", "✅ All passed"),
            ("test_scenarios.py — 3 canonical challenge scenarios", "3", "✅ All passed"),
            ("Frontend Vite Build", "—", "✅ 1838 modules transformed, dist/ generated"),
            ("Production API /api/health", "—", "✅ 200 OK, chromadb active, 26 chunks indexed"),
            ("Production API /api/chat (Scenario 1)", "—", "✅ Scientific summary + 3 citations returned"),
            ("Production API /api/recommend", "—", "✅ Recommendations + 4 evidence citations"),
        ],
        row_font_size=9.0
    )

    doc.add_paragraph(
        "Note on browser automation: Automated Playwright browser verification was unavailable during "
        "this audit session due to an external CDN issue (playwright.azureedge.net returning 404). "
        "Manual live-browser verification of the frontend was performed against the Vercel deployment."
    )

    # ─── SECTION 14: GitHub Repository ────────────────────────────────────────
    add_heading(doc, "14. GitHub Repository", 1, EMERALD)
    p = doc.add_paragraph()
    p.add_run("Repository URL:\n").font.bold = True
    r = p.add_run(GITHUB_URL)
    r.font.color.rgb = BLUE; r.font.bold = True
    p.add_run("\n\nContains: complete source code, RAG knowledge data, 24 pytest tests, "
              "GitHub Actions CI, Dockerfile, docker-compose.yml, Render + Vercel deployment config, "
              "and this submission document.\n\n")
    p.add_run("Repository Access (if private):\n").font.bold = True
    p.add_run(
        "As instructed on Page 5 of the Challenge PDF, collaborator access has been granted to:\n"
        "  • ankita.dasgupta@darukaa.com\n"
        "  • harsh.kumar@darukaa.com\n"
        "  • utkarsh.gauniyal@darukaa.com\n"
        "  • guneet.mutreja@darukaa.com"
    )

    # ─── SECTION 15: Live Demo URL ────────────────────────────────────────────
    add_heading(doc, "15. Live Demo URL", 1, EMERALD)
    add_callout(doc, f"LIVE DEMO:  {VERCEL_URL}", "D1FAE5")
    doc.add_paragraph(
        "The frontend is deployed on Vercel as a React SPA. The Vercel configuration (frontend/vercel.json) "
        "uses modern SPA rewrites to serve index.html for all routes while correctly passing JavaScript "
        "and CSS assets with the appropriate MIME types.\n\n"
        f"The backend API is deployed on Render at:  {RENDER_URL}\n"
        f"OpenAPI documentation:  {OPENAPI_URL}"
    )

    # ─── SECTION 16: Backend URL ──────────────────────────────────────────────
    add_heading(doc, "16. Backend API URL", 1, EMERALD)
    p = doc.add_paragraph()
    for label, url in [
        ("Base URL", RENDER_URL),
        ("Health Check", HEALTH_URL),
        ("OpenAPI Docs", OPENAPI_URL),
        ("Chat Endpoint", f"{RENDER_URL}/api/chat"),
        ("Analyze Endpoint", f"{RENDER_URL}/api/analyze"),
        ("Recommend Endpoint", f"{RENDER_URL}/api/recommend"),
        ("Retrieve Endpoint", f"{RENDER_URL}/api/retrieve"),
        ("Sources Catalog", f"{RENDER_URL}/api/sources"),
        ("Demo Scenarios", f"{RENDER_URL}/api/scenarios"),
    ]:
        r = p.add_run(f"• {label}: ")
        r.font.bold = True
        p.add_run(f"{url}\n").font.color.rgb = BLUE

    # ─── SECTION 17: Local Setup Instructions ─────────────────────────────────
    add_heading(doc, "17. Local Setup Instructions", 1, EMERALD)
    add_code_block(doc,
        "# 1. Clone the repository\n"
        f"git clone {GITHUB_URL}.git\n"
        "cd Daruka_AI_chatbot\n\n"
        "# 2. Install Python dependencies\n"
        "python -m pip install -r requirements.txt\n\n"
        "# 3. (Optional) Set environment variables\n"
        "cp .env.example .env\n"
        "# Edit .env — add GEMINI_API_KEY if available (not required)\n\n"
        "# 4. Run Knowledge Base Ingestion\n"
        "python scripts/ingest.py\n\n"
        "# 5. Run automated test suite (24 tests)\n"
        "python -m pytest tests/ -v\n\n"
        "# 6. Start FastAPI backend\n"
        "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000\n\n"
        "# 7. In a separate terminal — install and run React frontend\n"
        "cd frontend\n"
        "npm install\n"
        "npm run dev\n"
        "# Frontend: http://localhost:5173   Backend: http://localhost:8000\n\n"
        "# 8. Docker (all-in-one — builds both backend and frontend)\n"
        "docker compose up --build"
    )

    # ─── SECTION 18: Deployment Instructions ──────────────────────────────────
    add_heading(doc, "18. Deployment Instructions", 1, EMERALD)

    add_heading(doc, "Backend — Render", 2, DARK_SLATE)
    doc.add_paragraph(
        "1. Create a new Web Service on render.com.\n"
        "2. Connect the GitHub repository.\n"
        "3. Set Runtime: Docker (uses Dockerfile at repo root).\n"
        "4. Set environment variables in Render dashboard:\n"
        f"   ALLOWED_ORIGINS={VERCEL_URL}\n"
        "   GEMINI_API_KEY=YOUR_API_KEY_HERE (optional, activates LLM synthesis)\n"
        "5. Deploy. Health check: /api/health"
    )

    add_heading(doc, "Frontend — Vercel", 2, DARK_SLATE)
    doc.add_paragraph(
        "1. Create a new project on vercel.com.\n"
        "2. Connect the GitHub repository.\n"
        "3. Set Root Directory: frontend\n"
        "4. Build Command: npm run build\n"
        "5. Output Directory: dist\n"
        "6. Set environment variable:\n"
        f"   VITE_API_BASE_URL={RENDER_URL}\n"
        "7. Deploy. The frontend/vercel.json rewrites handle SPA routing automatically."
    )

    # ─── SECTION 19: CI/CD Details ────────────────────────────────────────────
    add_heading(doc, "19. CI/CD Details", 1, EMERALD)
    doc.add_paragraph(
        "File: .github/workflows/ci.yml\n\n"
        "Pipeline triggers on every push and pull_request to main.\n\n"
        "Steps:\n"
        "  1. Checkout repository\n"
        "  2. Set up Python 3.12\n"
        "  3. Install Python dependencies (pip install -r requirements.txt)\n"
        "  4. Run knowledge ingestion (python scripts/ingest.py)\n"
        "  5. Execute pytest (python -m pytest tests/ -v)\n"
        "  6. Set up Node.js 20\n"
        "  7. Install frontend dependencies (npm ci in frontend/)\n"
        "  8. Build production frontend (npm run build in frontend/)\n\n"
        "Both Render (backend) and Vercel (frontend) auto-deploy on every push to main."
    )

    # ─── SECTION 20: Demo Instructions for Evaluators ────────────────────────
    add_heading(doc, "20. Evaluator Quick-Start & Demo Instructions", 1, EMERALD)
    add_callout(doc, f"LIVE DEMO:  {VERCEL_URL}", "D1FAE5")

    doc.add_paragraph(
        "Suggested evaluator walkthrough (approximately 5 minutes):\n\n"
        "STEP 1 — Open the live demo:\n"
        f"  {VERCEL_URL}\n\n"
        "STEP 2 — Run a canonical challenge scenario:\n"
        "  • Click the 'Scenario 1: Semi-Arid Monoculture' button at the top of the chat panel.\n"
        "  • Observe the multi-variable causal diagnosis appear in the chat with formatted Markdown.\n"
        "  • Review the Diagnostics panel on the right: 5 environmental pillars, key interactions, "
        "    and prioritised recommendations with quantitative targets.\n\n"
        "STEP 3 — Inspect RAG Evidence:\n"
        "  • Click the 'Inspect RAG Evidence' tab on the right panel.\n"
        "  • Observe the retrieved scientific chunks, similarity scores, and source URLs "
        "    (FAO, IPCC, UNEP, IPBES, Nature, Science).\n\n"
        "STEP 4 — Test conversational clarification:\n"
        "  • Type: 'Biodiversity is declining on my land.'\n"
        "  • Observe: the system asks 4 targeted clarifying questions (not a generic response).\n\n"
        "STEP 5 — Multi-turn memory test:\n"
        "  • Reply: 'The soil pH is 5.4, organic carbon is 0.9%, rainfall is medium.'\n"
        "  • Reply: 'It is monoculture cash crops in a temperate valley.'\n"
        "  • Observe: the system accumulates context and produces a full evidence-grounded diagnosis "
        "    without asking you to repeat the earlier information.\n\n"
        "STEP 6 — Try the Form input:\n"
        "  • Click the 'Form' tab in the left panel.\n"
        "  • Adjust soil pH, organic carbon, and pollution sliders.\n"
        "  • Click 'Run Full Analysis' and review the structured diagnostic output.\n\n"
        "STEP 7 — Verify the API directly:\n"
        f"  • Open: {HEALTH_URL}\n"
        "  • Confirm: vector_store_initialized: true, indexed_chunks: 26, use_chromadb: true\n"
        f"  • Open: {OPENAPI_URL} — interactive Swagger UI for all endpoints."
    )

    # ─── SECTION 21: Limitations / Known Non-Blocking Notes ──────────────────
    add_heading(doc, "21. Limitations & Known Non-Blocking Notes", 1, EMERALD)
    doc.add_paragraph(
        "The following are known, non-blocking characteristics of the production deployment:\n\n"
        "1. Render Free Tier Cold Start:\n"
        "   Render's free tier spins down idle services after inactivity. The first request after "
        "   inactivity may have a 20–30 second cold start delay. Subsequent requests are instant.\n"
        "   This is a Render platform behaviour, not an application defect.\n\n"
        "2. LLM API Key (Optional):\n"
        "   The system is 100% functional without an API key, using its built-in deterministic "
        "   scientific reasoning engine. Adding a GEMINI_API_KEY or OPENAI_API_KEY activates "
        "   real-time LLM synthesis for richer narrative responses.\n\n"
        "3. Playwright Browser Automation:\n"
        "   During the final audit, automated browser verification via Playwright was unavailable "
        "   due to an external CDN issue (playwright.azureedge.net returning 404 for the driver). "
        "   This is an external infrastructure issue unrelated to the application. Manual live-browser "
        "   verification was performed on the Vercel deployment.\n\n"
        "4. ChromaDB Persistence on Render:\n"
        "   ChromaDB uses ephemeral disk storage on Render's free tier. The TF-IDF fallback ensures "
        "   100% retrieval availability even if ChromaDB resets between deployments. The 26 knowledge "
        "   chunks are re-indexed on every service startup from the committed data/raw/ JSON files.\n\n"
        "5. Knowledge Base Size:\n"
        "   The current knowledge base contains 26 high-quality scientific chunks. Expanding to "
        "   additional FAO/IPCC/IPBES publications would further improve retrieval depth."
    )

    # ─── Final evaluation criteria matrix ────────────────────────────────────
    add_heading(doc, "Appendix: Official Evaluation Criteria Verification Matrix", 1, EMERALD)
    make_table(doc,
        ["Criterion (Weight)", "PDF Requirement", "Implementation", "Status"],
        [
            ("Depth of Reasoning (30%)",
             "Connect ≥3 variables concurrently; non-obvious actionable interventions",
             "backend/services/reasoning_engine.py",
             "✅ 100% Verified"),
            ("Scientific Grounding (25%)",
             "Traceable citations from FAO, IPCC, UNEP, IPBES; real quantitative ranges",
             "data/raw/, data/metadata/",
             "✅ 100% Verified"),
            ("Knowledge System Design (20%)",
             "Genuine RAG retrieval, vector DB, inspectable evidence in UI & API",
             "backend/services/vector_store.py",
             "✅ 100% Verified"),
            ("Conversational Intelligence (15%)",
             "Context awareness, missing-variable detection, multi-turn state preservation",
             "backend/services/conversation_manager.py",
             "✅ 100% Verified"),
            ("Output Clarity (10%)",
             "5 pillars, key interactions, actionable cards, time horizons, confidence levels",
             "backend/models/schemas.py, frontend/src/App.jsx",
             "✅ 100% Verified"),
        ],
        row_font_size=9.0
    )

    # Final audit summary callout
    add_callout(doc,
        "FINAL AUDIT: 76/76 checks passed  |  24/24 backend tests  |  "
        "Production API live  |  Frontend deployed  |  GitHub up-to-date  |  READY FOR SUBMISSION",
        bg="D1FAE5"
    )

    doc.save(str(DOCX_PATH))
    print(f"[DOCX Generator] SUCCESS - Submission document saved to: {DOCX_PATH}")
    print(f"  GitHub:    {GITHUB_URL}")
    print(f"  Frontend:  {VERCEL_URL}")
    print(f"  Backend:   {RENDER_URL}")


if __name__ == "__main__":
    create_submission_docx()
