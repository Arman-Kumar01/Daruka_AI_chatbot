import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_multi_turn_conversation_accumulation():
    # Turn 1: User introduces problem and provides soil data
    t1_resp = client.post("/api/chat", json={
        "message": "Biodiversity is declining on my land. My soil organic carbon is 0.3% and pH is 6.2."
    })
    assert t1_resp.status_code == 200
    t1_data = t1_resp.json()
    session_id = t1_data["session_id"]
    assert session_id is not None
    # Still missing rainfall, land use, region
    assert t1_data["missing_information"] is not None
    assert any("Rainfall" in m for m in t1_data["missing_information"])

    # Turn 2: User provides rainfall
    t2_resp = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "The rainfall is low with prolonged dry periods."
    })
    assert t2_resp.status_code == 200
    t2_data = t2_resp.json()
    assert t2_data["session_id"] == session_id

    # Turn 3: User provides land use and region
    t3_resp = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "I am farming monoculture wheat in a semi-arid dryland region."
    })
    assert t3_resp.status_code == 200
    t3_data = t3_resp.json()
    
    # Now all variables are combined: recommendations should be fully generated!
    assert len(t3_data["recommendations"]) >= 1
    assert t3_data["environmental_assessment"]["soil"]["ph"] == 6.2
    assert "0.3" in str(t3_data["environmental_assessment"]["soil"]["organic_carbon_percent"])
    assert "low" in t3_data["environmental_assessment"]["climate"]["rainfall"].lower()
    assert "monoculture wheat" in t3_data["environmental_assessment"]["land_use"]["current_practice"].lower()
    assert "semi-arid" in t3_data["environmental_assessment"]["climate"]["region"].lower()

    # Verify session inspection endpoint
    session_resp = client.get(f"/api/conversations/{session_id}")
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    assert len(session_data["messages"]) >= 6  # 3 user turns + 3 assistant responses
    assert session_data["cumulative_state"]["soil"]["organic_carbon_percent"] == 0.3
    assert session_data["cumulative_state"]["land_use"] == "monoculture wheat"
