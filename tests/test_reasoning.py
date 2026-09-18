import pytest
from backend.services.reasoning_engine import reasoning_engine
from backend.services.vector_store import vector_store
from backend.models.schemas import EnvironmentalInput, SoilData, BiodiversityData, HumanImpactData


def test_multi_variable_reasoning_three_variables():
    # Scenario 1: SOC 0.3%, low rainfall, monoculture wheat, semi-arid
    env_input = EnvironmentalInput(
        region="semi-arid",
        soil=SoilData(ph=6.2, organic_carbon_percent=0.3, moisture_percent=12.0),
        rainfall="low",
        temperature_c=31.0,
        land_use="monoculture wheat",
        biodiversity=BiodiversityData(species_richness="low", habitat_diversity="low")
    )
    
    chunks = vector_store.retrieve("soil organic carbon monoculture wheat semi-arid", top_k=4)
    result = reasoning_engine.synthesize_assessment(env_input, chunks)
    
    # Assert environmental assessment structure
    assessment = result["environmental_assessment"]
    assert assessment.soil["status"] != ""
    assert "semi-arid" in assessment.climate["region"].lower()
    
    # Assert multi-variable interaction connecting >= 3 variables
    interactions = result["key_interactions"]
    assert len(interactions) >= 1
    # Check that interactions mention at least 3 distinct variables
    first_interaction = interactions[0].lower()
    assert any(term in first_interaction for term in ["carbon", "soc"])
    assert any(term in first_interaction for term in ["moisture", "rainfall", "water"])
    assert any(term in first_interaction for term in ["microbial", "biodiversity", "nitrogen"])
    
    # Assert recommendations quality
    recs = result["recommendations"]
    assert len(recs) >= 1
    for rec in recs:
        # Must handle at least 3 interacting variables
        assert len(rec.interacting_variables) >= 3
        # Must have concrete non-obvious action
        assert "cover crop" in rec.action.lower() or "agroforestry" in rec.action.lower()
        # Must have scientific mechanism
        assert len(rec.scientific_mechanism) > 30
        # Must have impacted metrics
        assert len(rec.impacted_metrics) >= 2
        # Must have time horizon
        assert any(h in rec.time_horizon.lower() for h in ["short", "medium", "long"])
        # Must have confidence
        assert "high" in rec.confidence.lower()
        # Must have evidence citations
        assert len(rec.evidence) > 0


def test_waterlogging_and_fragmentation_reasoning():
    # Scenario 2: High moisture (38%), agricultural floodplain, fragmented habitat
    env_input = EnvironmentalInput(
        region="agricultural floodplain",
        soil=SoilData(ph=6.8, moisture_percent=38.0),
        rainfall="high",
        land_use="intensive arable",
        biodiversity=BiodiversityData(habitat_diversity="fragmented isolated patches")
    )
    chunks = vector_store.retrieve("agricultural waterlogging bioswales riparian", top_k=4)
    result = reasoning_engine.synthesize_assessment(env_input, chunks)
    
    recs = result["recommendations"]
    assert len(recs) >= 1
    rec_texts = [r.action.lower() for r in recs]
    assert any("bioswale" in t or "wetland" in t for t in rec_texts)
