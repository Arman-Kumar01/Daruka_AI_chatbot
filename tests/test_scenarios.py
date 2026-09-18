import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_scenario_1_semi_arid_monoculture():
    """
    Scenario 1: Low soil organic carbon + low rainfall + monoculture wheat + semi-arid region
    Expected: Intercropping / agroforestry / cover crops, soil carbon improvement estimates, FAO / IPCC citations.
    """
    payload = {
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
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assert multi-variable reasoning output
    actions = [r["action"].lower() for r in data["recommendations"]]
    assert any("cover crop" in a or "agroforestry" in a for a in actions)
    
    # Assert quantitative improvement ranges cited
    all_metrics = [m for r in data["recommendations"] for m in r["impacted_metrics"]]
    assert any("organic carbon" in m.lower() for m in all_metrics)
    
    # Assert credible evidence cited
    orgs = [e["organization"] for e in data["evidence"]]
    assert any("FAO" in o or "IPCC" in o for o in orgs)


def test_scenario_2_waterlogging_and_fragmentation():
    """
    Scenario 2: High soil moisture + habitat fragmentation + low species richness + agricultural land
    Expected: Vegetated bioswales, corridors, redox recovery, wetland biodiversity.
    """
    payload = {
        "region": "agricultural floodplain",
        "soil": {
            "ph": 6.8,
            "organic_carbon_percent": 1.4,
            "moisture_percent": 38.0
        },
        "land_use": "intensive arable",
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
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    actions = [r["action"].lower() for r in data["recommendations"]]
    assert any("bioswale" in a or "wetland" in a or "riparian" in a for a in actions)


def test_scenario_3_chemical_pollution_and_pollinators():
    """
    Scenario 3: High pollution + declining biodiversity + reduced vegetation / habitat diversity
    Expected: Vegetative buffer strips, pesticide phytoremediation, wildflower margins, UNEP citations.
    """
    payload = {
        "region": "temperate intensive farming valley",
        "soil": {
            "ph": 5.4,
            "organic_carbon_percent": 0.9,
            "moisture_percent": 21.0
        },
        "land_use": "cash crop monoculture",
        "rainfall": "medium",
        "temperature_c": 26.0,
        "biodiversity": {
            "species_richness": "low",
            "habitat_diversity": "low",
            "pollinator_presence": "severe collapse"
        },
        "human_impact": {
            "pollution": "high pesticide runoff",
            "deforestation": "low"
        }
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    actions = [r["action"].lower() for r in data["recommendations"]]
    assert any("vegetative filter" in a or "wildflower" in a or "margin" in a for a in actions)
    orgs = [e["organization"] for e in data["evidence"]]
    assert any("UNEP" in o or "Environmental" in o for o in orgs)
