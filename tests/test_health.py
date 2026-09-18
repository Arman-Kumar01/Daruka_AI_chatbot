import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["vector_store_initialized"] is True
    assert data["indexed_chunks"] > 0


def test_sources_catalog_endpoint():
    response = client.get("/api/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert data["total"] > 0
    # Check that authoritative sources are present
    orgs = [s["organization"] for s in data["sources"]]
    assert any("FAO" in o for o in orgs)
    assert any("IPCC" in o for o in orgs)
    assert any("UNEP" in o for o in orgs)


def test_demo_scenarios_endpoint():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 3


def test_recommend_endpoint():
    payload = {
        "region": "semi-arid",
        "soil": {"organic_carbon_percent": 0.3},
        "rainfall": "low",
        "land_use": "monoculture wheat"
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) >= 1
    assert len(data["key_interactions"]) >= 1


def test_ingest_endpoint():
    response = client.post("/api/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_chunks"] >= 26
