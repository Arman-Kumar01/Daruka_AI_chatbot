import pytest
from backend.services.reasoning_engine import reasoning_engine
from backend.services.vector_store import vector_store
from backend.models.schemas import EnvironmentalInput, SoilData


def test_evidence_presence_and_validity():
    env_input = EnvironmentalInput(
        region="semi-arid",
        soil=SoilData(organic_carbon_percent=0.3),
        rainfall="low",
        land_use="monoculture wheat"
    )
    chunks = vector_store.retrieve("soil organic carbon legume cover crops semi-arid", top_k=4)
    result = reasoning_engine.synthesize_assessment(env_input, chunks)
    
    evidence_list = result["evidence"]
    assert len(evidence_list) > 0
    
    for ev in evidence_list:
        assert ev.title != ""
        assert any(
            org in ev.organization
            for org in ["FAO", "IPCC", "UNEP", "IPBES", "Nature", "Science", "Applied Ecology", "Environmental"]
        )
        assert ev.year >= 2017
        assert ev.url.startswith("http")
        assert len(ev.finding) > 20
