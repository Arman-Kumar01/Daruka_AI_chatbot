import pytest
from backend.services.vector_store import vector_store


def test_retrieval_soil_organic_carbon():
    query = "soil organic carbon legume cover crops semi-arid"
    chunks = vector_store.retrieve(query, top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert top.score > 0.1
    # Should retrieve FAO or Nature cover crops paper
    assert any(term in top.title.lower() or term in top.text.lower() for term in ["carbon", "cover crop", "microbial"])
    assert top.organization != ""
    assert top.year > 2000
    assert top.url != ""


def test_retrieval_agroforestry():
    query = "agroforestry biodiversity microclimate temperature reduction"
    chunks = vector_store.retrieve(query, top_k=3)
    assert len(chunks) > 0
    # Should retrieve IPCC SRCCL Chapter 4
    orgs = [c.organization for c in chunks]
    assert any("IPCC" in o for o in orgs)


def test_retrieval_pollution():
    query = "pesticide pollution runoff floral strips pollinators"
    chunks = vector_store.retrieve(query, top_k=3)
    assert len(chunks) > 0
    orgs = [c.organization for c in chunks]
    assert any("UNEP" in o or "Environmental" in o for o in orgs)


def test_retrieval_empty_query():
    chunks = vector_store.retrieve("", top_k=3)
    # Should safely return empty or top fallback without exception
    assert isinstance(chunks, list)
