import pytest
from backend.services.clarification_service import clarification_service
from backend.models.schemas import EnvironmentalInput, SoilData, BiodiversityData


def test_missing_field_detection_incomplete():
    # Only 1 variable provided
    env_input = EnvironmentalInput(
        soil=SoilData(organic_carbon_percent=0.3)
    )
    is_sufficient, missing_labels, questions = clarification_service.analyze_completeness(env_input)
    assert is_sufficient is False
    assert len(missing_labels) >= 3
    assert any("Rainfall" in label for label in missing_labels)
    assert any("land-use" in label.lower() for label in missing_labels)
    assert len(questions) >= 3


def test_missing_field_detection_sufficient():
    # 4 variables provided: SOC, rainfall, land use, region
    env_input = EnvironmentalInput(
        region="semi-arid",
        soil=SoilData(organic_carbon_percent=0.3, ph=6.2),
        rainfall="low",
        land_use="monoculture wheat"
    )
    is_sufficient, missing_labels, questions = clarification_service.analyze_completeness(env_input)
    assert is_sufficient is True


def test_missing_field_detection_empty():
    env_input = EnvironmentalInput()
    is_sufficient, missing_labels, questions = clarification_service.analyze_completeness(env_input)
    assert is_sufficient is False
    assert len(missing_labels) >= 4
