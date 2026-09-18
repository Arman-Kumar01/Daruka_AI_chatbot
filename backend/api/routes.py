"""
API Route Handlers for Darukaa.Earth AI Biodiversity Intelligence System.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import (
    ChatRequest,
    StructuredResponse,
    EnvironmentalInput,
    RecommendationItem,
    RetrieveRequest,
    RetrieveResponse,
    EvidenceCitation
)
from backend.services.conversation_manager import conversation_manager
from backend.services.clarification_service import clarification_service
from backend.services.vector_store import vector_store
from backend.services.reasoning_engine import reasoning_engine
from backend.services.llm_adapter import llm_adapter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint indicating RAG vector store and service readiness."""
    return {
        "status": "healthy",
        "service": "Darukaa AI Biodiversity Intelligence System",
        "vector_store_initialized": vector_store.initialized,
        "indexed_chunks": len(vector_store.chunks),
        "use_chromadb": vector_store.use_chroma
    }


@router.get("/sources")
async def list_sources():
    """Returns the peer-reviewed and authoritative scientific sources catalog."""
    return {
        "sources": vector_store.get_all_sources(),
        "total": len(vector_store.get_all_sources())
    }


@router.get("/scenarios")
async def get_demo_scenarios():
    """Returns canonical test scenarios matching the hackathon challenge specifications."""
    return {
        "scenarios": [
            {
                "id": "scenario-1",
                "name": "Scenario 1: Semi-Arid Monoculture Depletion",
                "description": "Low soil organic carbon (0.3%) + Low rainfall + Monoculture wheat + Semi-arid region",
                "data": {
                    "region": "semi-arid",
                    "soil": {
                        "ph": 6.2,
                        "organic_carbon_percent": 0.3,
                        "moisture_percent": 12.0
                    },
                    "land_use": "monoculture wheat",
                    "rainfall": "low",
                    "temperature_c": 31.0,
                    "biodiversity": {
                        "species_richness": "low",
                        "habitat_diversity": "low"
                    },
                    "human_impact": {
                        "pollution": "medium",
                        "deforestation": "low"
                    }
                }
            },
            {
                "id": "scenario-2",
                "name": "Scenario 2: Waterlogged Agricultural Habitat Fragmentation",
                "description": "High soil moisture (38%) + Habitat fragmentation + Low species richness + Agricultural floodplain",
                "data": {
                    "region": "lowland agricultural floodplain",
                    "soil": {
                        "ph": 6.8,
                        "organic_carbon_percent": 1.4,
                        "moisture_percent": 38.0
                    },
                    "land_use": "continuous intensive arable",
                    "rainfall": "high",
                    "temperature_c": 22.0,
                    "biodiversity": {
                        "species_richness": "low",
                        "habitat_diversity": "fragmented isolated patches"
                    },
                    "human_impact": {
                        "pollution": "low",
                        "deforestation": "medium"
                    }
                }
            },
            {
                "id": "scenario-3",
                "name": "Scenario 3: Agrochemical Pollution & Pollinator Collapse",
                "description": "High chemical runoff / pesticide pollution + Declining pollinators + Reduced riparian buffer",
                "data": {
                    "region": "temperate intensive farming valley",
                    "soil": {
                        "ph": 5.4,
                        "organic_carbon_percent": 0.9,
                        "moisture_percent": 21.0
                    },
                    "land_use": "monoculture cash crops",
                    "rainfall": "medium",
                    "temperature_c": 26.0,
                    "biodiversity": {
                        "species_richness": "low",
                        "habitat_diversity": "low",
                        "pollinator_presence": "severe collapse"
                    },
                    "human_impact": {
                        "pollution": "high pesticide and fertilizer runoff",
                        "deforestation": "low",
                        "pesticide_intensity": "high"
                    }
                }
            }
        ]
    }


@router.post("/retrieve", response_model=RetrieveResponse)
async def semantic_retrieve(req: RetrieveRequest):
    """Direct semantic retrieval endpoint for inspectability and evaluator testing."""
    chunks = vector_store.retrieve(
        query=req.query,
        top_k=req.top_k,
        variables_filter=req.variables_filter
    )
    return RetrieveResponse(
        query=req.query,
        chunks=chunks,
        total_retrieved=len(chunks)
    )


@router.post("/chat", response_model=StructuredResponse)
async def chat_interaction(req: ChatRequest):
    """
    Multi-turn conversational intelligence endpoint.
    Maintains conversational memory, detects missing environmental variables,
    and returns evidence-grounded scientific diagnostics.
    """
    session = conversation_manager.get_or_create_session(req.session_id)
    
    # 1. Parse and accumulate inputs
    if req.message:
        session.add_message("user", req.message)
        parsed_from_text = conversation_manager.parse_natural_language(req.message)
        session.merge_input(parsed_from_text)

    if req.structured_input:
        session.merge_input(req.structured_input)

    current_state = session.cumulative_state

    # 2. Check completeness across 5 core pillars
    is_sufficient, missing_labels, clarifying_questions = clarification_service.analyze_completeness(current_state)

    # If minimally insufficient (e.g. user just said "Biodiversity is declining on my land"),
    # ask targeted clarifying questions while providing the preliminary ecological scope
    if not is_sufficient and req.message and not req.structured_input:
        clarification_msg = (
            "To formulate an accurate multi-variable ecological diagnosis, I need a few key environmental indicators:\n\n"
            + "\n".join([f"{i+1}. {q}" for i, q in enumerate(clarifying_questions[:4])])
        )
        session.add_message("assistant", clarification_msg)
        
        # Build provisional empty/partial assessment
        provisional = reasoning_engine.synthesize_assessment(current_state, [])
        return StructuredResponse(
            session_id=session.session_id,
            environmental_assessment=provisional["environmental_assessment"],
            key_interactions=[
                "Insufficient multi-variable data: awaiting soil health, land use, and rainfall parameters to trace causal mechanisms."
            ],
            recommendations=[],
            evidence=[],
            missing_information=missing_labels,
            clarifying_questions=clarifying_questions,
            scientific_summary=clarification_msg,
            retrieval_metadata={"status": "awaiting_sufficient_variables"}
        )

    # 3. Retrieve relevant scientific literature from knowledge layer
    query_terms = [
        current_state.region or "",
        current_state.land_use or "",
        current_state.rainfall or "",
        "soil organic carbon" if current_state.soil and current_state.soil.organic_carbon_percent else "",
        "waterlogging" if current_state.soil and current_state.soil.moisture_percent and current_state.soil.moisture_percent > 30 else "",
        "pollution" if current_state.human_impact and current_state.human_impact.pollution else "",
        req.message or ""
    ]
    retrieval_query = " ".join([t for t in query_terms if t])
    
    retrieved_chunks = vector_store.retrieve(
        query=retrieval_query,
        top_k=5
    )

    # 4. Multi-variable Causal Reasoning
    reasoning_data = reasoning_engine.synthesize_assessment(current_state, retrieved_chunks)

    # 5. Scientific Summary Generation (LLM or deterministic scientific synthesis)
    summary = await llm_adapter.generate_scientific_summary(
        current_state,
        retrieved_chunks,
        reasoning_data
    )

    session.add_message("assistant", summary)

    return StructuredResponse(
        session_id=session.session_id,
        environmental_assessment=reasoning_data["environmental_assessment"],
        key_interactions=reasoning_data["key_interactions"],
        recommendations=reasoning_data["recommendations"],
        evidence=reasoning_data["evidence"],
        missing_information=missing_labels if missing_labels else None,
        clarifying_questions=clarifying_questions if missing_labels else None,
        scientific_summary=summary,
        retrieval_metadata={
            "retrieval_query": retrieval_query,
            "chunks_retrieved": len(retrieved_chunks),
            "top_source": retrieved_chunks[0].title if retrieved_chunks else None,
            "similarity_score": retrieved_chunks[0].score if retrieved_chunks else 0.0
        }
    )


@router.post("/analyze", response_model=StructuredResponse)
async def analyze_structured(env_input: EnvironmentalInput):
    """Direct analysis endpoint for structured JSON input."""
    session = conversation_manager.get_or_create_session()
    session.merge_input(env_input)
    
    _, missing_labels, clarifying_questions = clarification_service.analyze_completeness(env_input)

    query_parts = [
        env_input.region or "",
        env_input.land_use or "",
        env_input.rainfall or "",
        "soil organic carbon" if env_input.soil and env_input.soil.organic_carbon_percent is not None else "",
        "waterlogging drainage bioswales" if env_input.soil and env_input.soil.moisture_percent and env_input.soil.moisture_percent > 30 else "",
        "pesticide pollution chemical runoff wildflower margins" if env_input.human_impact and env_input.human_impact.pollution else ""
    ]
    query_str = " ".join([p for p in query_parts if p]).strip() or "soil carbon biodiversity restoration"
    retrieved_chunks = vector_store.retrieve(query=query_str, top_k=5)
    
    reasoning_data = reasoning_engine.synthesize_assessment(env_input, retrieved_chunks)
    summary = await llm_adapter.generate_scientific_summary(env_input, retrieved_chunks, reasoning_data)

    return StructuredResponse(
        session_id=session.session_id,
        environmental_assessment=reasoning_data["environmental_assessment"],
        key_interactions=reasoning_data["key_interactions"],
        recommendations=reasoning_data["recommendations"],
        evidence=reasoning_data["evidence"],
        missing_information=missing_labels if missing_labels else None,
        clarifying_questions=clarifying_questions if missing_labels else None,
        scientific_summary=summary,
        retrieval_metadata={
            "query": query_str,
            "chunks_count": len(retrieved_chunks)
        }
    )


@router.post("/recommend")
async def generate_recommendations(env_input: EnvironmentalInput):
    """Direct recommendations endpoint returning actionable multi-variable ecological interventions."""
    query_parts = [
        env_input.region or "",
        env_input.land_use or "",
        env_input.rainfall or "",
        "soil organic carbon" if env_input.soil and env_input.soil.organic_carbon_percent is not None else "",
        "waterlogging drainage bioswales" if env_input.soil and env_input.soil.moisture_percent and env_input.soil.moisture_percent > 30 else "",
        "pesticide pollution chemical runoff wildflower margins" if env_input.human_impact and env_input.human_impact.pollution else ""
    ]
    query_str = " ".join([p for p in query_parts if p]).strip() or "soil carbon biodiversity restoration"
    retrieved_chunks = vector_store.retrieve(query=query_str, top_k=5)
    reasoning_data = reasoning_engine.synthesize_assessment(env_input, retrieved_chunks)
    
    return {
        "status": "success",
        "recommendations": reasoning_data["recommendations"],
        "key_interactions": reasoning_data["key_interactions"],
        "evidence": reasoning_data["evidence"]
    }


@router.post("/ingest")
async def trigger_ingestion():
    """Triggers knowledge ingestion pipeline and refreshes vector index."""
    from scripts.ingest import run_ingestion
    chunks = run_ingestion()
    vector_store._initialize()
    return {
        "status": "success",
        "message": "Knowledge base ingested and vector index refreshed.",
        "total_chunks": len(chunks)
    }


@router.get("/conversations/{session_id}")
async def get_conversation(session_id: str):
    """Retrieves full conversation history and accumulated environmental state."""
    if session_id not in conversation_manager.sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")
    session = conversation_manager.sessions[session_id]
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "cumulative_state": session.cumulative_state,
        "messages": session.messages
    }
