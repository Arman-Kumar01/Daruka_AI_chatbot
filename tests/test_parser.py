import pytest
from backend.services.conversation_manager import conversation_manager
from backend.models.schemas import EnvironmentalInput, SoilData


def test_parse_natural_language_full():
    query = "In a semi-arid region, my soil organic carbon is 0.3%, pH is 6.2, soil moisture is 12%, rainfall is low, temperature is 31°C, and crop is monoculture wheat."
    parsed = conversation_manager.parse_natural_language(query)
    
    assert parsed.region == "semi-arid"
    assert parsed.soil is not None
    assert parsed.soil.organic_carbon_percent == 0.3
    assert parsed.soil.ph == 6.2
    assert parsed.soil.moisture_percent == 12.0
    assert parsed.rainfall == "low"
    assert parsed.temperature_c == 31.0
    assert "monoculture" in parsed.land_use.lower()


def test_parse_natural_language_partial():
    query = "Soil organic carbon is 0.4% and rainfall is low."
    parsed = conversation_manager.parse_natural_language(query)
    
    assert parsed.soil.organic_carbon_percent == 0.4
    assert parsed.rainfall == "low"
    assert parsed.soil.ph is None
    assert parsed.land_use is None


def test_parse_coordinates():
    query = "Field located at lat: 31.5, lon: 35.2 with declining biodiversity"
    parsed = conversation_manager.parse_natural_language(query)
    
    assert parsed.coordinates is not None
    assert parsed.coordinates.latitude == 31.5
    assert parsed.coordinates.longitude == 35.2
    assert parsed.biodiversity.species_richness == "low"


def test_parse_empty_input():
    parsed = conversation_manager.parse_natural_language("")
    assert parsed.region is None
    assert parsed.soil is None
    assert parsed.rainfall is None


def test_parse_invalid_values():
    query = "pH is 99 and temperature is freezing cold with 1000% carbon"
    parsed = conversation_manager.parse_natural_language(query)
    # pH 99 should be rejected by bounds check
    assert parsed.soil is None or parsed.soil.ph is None
