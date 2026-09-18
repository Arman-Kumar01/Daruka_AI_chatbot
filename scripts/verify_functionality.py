"""
Comprehensive Full-Functionality Verification Script for Darukaa.Earth AI Platform.
Tests all requirements, constraints, and use cases from the official Challenge PDF.
"""

import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"


def request(endpoint: str, method: str = "GET", payload: dict = None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def test_suite():
    print("=" * 70)
    print("DARUKAA.EARTH AI BIODIVERSITY PLATFORM — PDF REQUIREMENT AUDIT")
    print("=" * 70)

    # 1. Health & Vector Store
    status, health = request("/api/health")
    print(f"\n[1] Health Endpoint: HTTP {status}")
    print(f"    - Vector Store Active: {health.get('vector_store_initialized')}")
    print(f"    - Indexed Chunks: {health.get('indexed_chunks')} authentic literature chunks")
    assert health.get("indexed_chunks") >= 26, "Expected at least 26 indexed chunks"

    # 2. Knowledge System: Check Authors & Organizations (FAO, IPCC, UNEP, IPBES)
    status, sources_data = request("/api/sources")
    sources = sources_data.get("sources", [])
    orgs = set(s.get("organization") for s in sources)
    print(f"\n[2] Knowledge System: HTTP {status} — Found {len(sources)} Sources")
    print(f"    - Indexed Organizations: {', '.join(orgs)}")
    assert any("FAO" in o for o in orgs), "Missing FAO source"
    assert any("IPCC" in o for o in orgs), "Missing IPCC source"
    assert any("UNEP" in o for o in orgs), "Missing UNEP source"

    # 3. PDF Page 3 Example Use Case
    print("\n[3] Testing PDF Page 3 Canonical Use Case:")
    print("    Input: SOC: 0.3%, Rainfall: low, Crop: monoculture wheat, Region: semi-arid")
    p3_payload = {
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
        }
    }
    status, p3_result = request("/api/analyze", method="POST", payload=p3_payload)
    print(f"    - Response Status: HTTP {status}")
    print(f"    - Environmental Assessment Pillars: {list(p3_result.get('environmental_assessment', {}).keys())}")
    
    interactions = p3_result.get("key_interactions", [])
    print(f"    - Multi-Variable Interactions ({len(interactions)} found):")
    for i, inter in enumerate(interactions):
        print(f"      [{i+1}] {inter[:120]}...")

    recs = p3_result.get("recommendations", [])
    print(f"    - Actionable Recommendations ({len(recs)} generated):")
    for i, rec in enumerate(recs):
        print(f"      [{i+1}] Action: {rec.get('action')}")
        print(f"          Mechanism: {rec.get('scientific_mechanism')[:100]}...")
        print(f"          Metrics: {rec.get('impacted_metrics')}")
        print(f"          Time Horizon: {rec.get('time_horizon')} | Confidence: {rec.get('confidence')}")
        print(f"          Interacting Variables: {rec.get('interacting_variables')}")
        print(f"          Evidence Source: {[e.get('organization') for e in rec.get('evidence', [])]}")

    # Assertions for Page 3
    assert len(recs) >= 2, "Expected at least 2 recommendations for Scenario 1"
    rec_texts = [r["action"].lower() for r in recs]
    assert any("cover crop" in t or "agroforestry" in t or "intercrop" in t for t in rec_texts), "Must recommend cover crops / agroforestry / intercropping"
    all_metrics = [m for r in recs for m in r["impacted_metrics"]]
    assert any("organic carbon" in m.lower() for m in all_metrics), "Must provide measurable carbon improvement estimates"
    evidence_orgs = [e.get("organization") for e in p3_result.get("evidence", [])]
    assert any("FAO" in o for o in evidence_orgs), "Must reference FAO"
    assert any("IPCC" in o for o in evidence_orgs), "Must reference IPCC"

    # 4. Multi-Turn Conversational Memory & Clarification
    print("\n[4] Testing Conversational Intelligence & Memory (PDF Page 2):")
    # Turn 1: User gives incomplete observation
    t1_payload = {"message": "Biodiversity is declining on my land."}
    status, t1_res = request("/api/chat", method="POST", payload=t1_payload)
    session_id = t1_res.get("session_id")
    print(f"    - Turn 1: Incomplete query sent.")
    print(f"      Missing Information Detected: {t1_res.get('missing_information')}")
    print(f"      Clarifying Questions Asked: {len(t1_res.get('clarifying_questions', []))}")
    assert t1_res.get("missing_information") is not None, "System should detect missing fields"
    assert len(t1_res.get("clarifying_questions", [])) >= 3, "System must ask clarifying questions"

    # Turn 2: User provides soil
    t2_payload = {"session_id": session_id, "message": "My soil organic carbon is 0.3% and pH is 6.2."}
    status, t2_res = request("/api/chat", method="POST", payload=t2_payload)
    print(f"    - Turn 2: Soil data provided. Retaining session {session_id}.")

    # Turn 3: User provides rainfall
    t3_payload = {"session_id": session_id, "message": "Rainfall is low."}
    status, t3_res = request("/api/chat", method="POST", payload=t3_payload)
    print(f"    - Turn 3: Rainfall provided.")

    # Turn 4: User provides land use and region
    t4_payload = {"session_id": session_id, "message": "The crop is monoculture wheat in a semi-arid region."}
    status, t4_res = request("/api/chat", method="POST", payload=t4_payload)
    print(f"    - Turn 4: Final variables supplied.")
    print(f"      Assessment Soil pH: {t4_res['environmental_assessment']['soil']['ph']}")
    print(f"      Assessment SOC: {t4_res['environmental_assessment']['soil']['organic_carbon_percent']}")
    print(f"      Assessment Rainfall: {t4_res['environmental_assessment']['climate']['rainfall']}")
    print(f"      Assessment Land Use: {t4_res['environmental_assessment']['land_use']['current_practice']}")
    print(f"      Final Recommendations: {len(t4_res.get('recommendations', []))}")
    assert t4_res["environmental_assessment"]["soil"]["ph"] == 6.2, "Turn 2 soil pH was forgotten!"
    assert len(t4_res.get("recommendations", [])) >= 1, "Expected recommendations after full context is assembled"

    # Check conversation endpoint
    status, conv = request(f"/api/conversations/{session_id}")
    print(f"    - Inspect Session API: HTTP {status} — Total messages in memory: {len(conv.get('messages', []))}")
    assert len(conv.get("messages", [])) == 8, "Expected 4 user messages + 4 assistant responses in memory"

    # 5. Direct Semantic Retrieval Inspectability
    print("\n[5] Testing RAG Retrieval Inspectability (/api/retrieve):")
    ret_payload = {"query": "biological nitrogen fixation legume cereal intercropping", "top_k": 3}
    status, ret_res = request("/api/retrieve", method="POST", payload=ret_payload)
    print(f"    - Retrieval Status: HTTP {status} — Found {ret_res.get('total_retrieved')} chunks")
    for chunk in ret_res.get("chunks", []):
        print(f"      • Score: {chunk.get('score')} | Org: {chunk.get('organization')} | Title: {chunk.get('title')}")
        print(f"        URL: {chunk.get('url')}")
    assert ret_res.get("total_retrieved") > 0, "Retrieval returned 0 chunks"

    # 6. Offline Spatial / Geo-Coordinates Bonus
    print("\n[6] Testing Offline Geo-Coordinates Resolution:")
    geo_payload = {
        "coordinates": {"latitude": 31.5, "longitude": 35.2},
        "soil": {"organic_carbon_percent": 0.4},
        "rainfall": "low",
        "land_use": "cereal farming"
    }
    status, geo_res = request("/api/analyze", method="POST", payload=geo_payload)
    inferred_biome = geo_res["environmental_assessment"]["climate"]["region"]
    print(f"    - Lat 31.5, Lon 35.2 -> Inferred Biome: {inferred_biome}")
    assert "dryland" in inferred_biome.lower() or "semi-arid" in inferred_biome.lower() or "mediterranean" in inferred_biome.lower()

    print("\n" + "=" * 70)
    print("ALL CHALLENGE PDF REQUIREMENTS FUNCTIONALLY VERIFIED!")
    print("=" * 70)


if __name__ == "__main__":
    test_suite()
