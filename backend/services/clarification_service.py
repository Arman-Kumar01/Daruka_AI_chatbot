"""
Clarification & Information Completeness Service.
Detects missing environmental variables that materially affect diagnostic precision
and generates targeted clarifying questions for multi-turn conversations.
"""

from typing import List, Tuple, Dict, Any, Optional
from backend.models.schemas import EnvironmentalInput


class ClarificationService:
    # Essential pillars required for comprehensive multi-variable diagnostic
    REQUIRED_FIELDS = [
        ("soil_organic_carbon", "Soil organic carbon (SOC) percentage", "Needed to determine soil biological activity and microbial water retention capacity."),
        ("soil_ph", "Soil pH", "Needed to assess nutrient bioavailability and earthworm/microbial viability."),
        ("rainfall", "Rainfall pattern or annual precipitation", "Required to distinguish between climate-driven drought stress and soil degradation."),
        ("land_use", "Current land use or crop type (e.g., monoculture wheat, agroforestry)", "Essential to evaluate crop rotation diversity and habitat fragmentation."),
        ("region", "Region or geographic biome (or coordinates)", "Defines baseline temperature, evapotranspiration, and soil classification.")
    ]

    def analyze_completeness(self, env_input: EnvironmentalInput) -> Tuple[bool, List[str], List[str]]:
        """
        Determines whether sufficient variables are present to formulate a multi-variable diagnosis.
        Returns:
            is_minimally_sufficient (bool): True if at least 3 distinct variables are known.
            missing_critical_labels (List[str]): Plain names of missing variables.
            clarifying_questions (List[str]): Targeted questions explaining why each field is needed.
        """
        known_variables = []

        # Check Soil variables
        if env_input.soil:
            if env_input.soil.organic_carbon_percent is not None:
                known_variables.append("soil_organic_carbon")
            if env_input.soil.ph is not None:
                known_variables.append("soil_ph")
            if env_input.soil.moisture_percent is not None:
                known_variables.append("soil_moisture")

        # Check Land use
        if env_input.land_use and env_input.land_use.strip():
            known_variables.append("land_use")

        # Check Climate
        if env_input.rainfall and env_input.rainfall.strip():
            known_variables.append("rainfall")
        if env_input.temperature_c is not None:
            known_variables.append("temperature")

        # Check Region / Spatial
        if env_input.region and env_input.region.strip():
            known_variables.append("region")
        elif env_input.coordinates and env_input.coordinates.latitude is not None:
            known_variables.append("region")

        # Check Biodiversity
        if env_input.biodiversity:
            if env_input.biodiversity.species_richness or env_input.biodiversity.habitat_diversity:
                known_variables.append("biodiversity_indicator")

        # Check Human Impact
        if env_input.human_impact:
            if env_input.human_impact.pollution or env_input.human_impact.deforestation:
                known_variables.append("human_impact")

        # Determine missing critical items
        missing_labels = []
        clarifying_questions = []

        if "soil_organic_carbon" not in known_variables:
            missing_labels.append("Soil organic carbon % (SOC)")
            clarifying_questions.append(
                "Can you provide your Soil Organic Carbon (SOC) percentage or approximate soil organic matter level? (This helps assess microbial carrying capacity and water retention)."
            )

        if "rainfall" not in known_variables:
            missing_labels.append("Rainfall pattern or seasonal precipitation")
            clarifying_questions.append(
                "What is your rainfall pattern or annual precipitation? (e.g., low/arid, seasonal monsoonal, or temperate regular)."
            )

        if "land_use" not in known_variables:
            missing_labels.append("Current land-use or crop management practice")
            clarifying_questions.append(
                "What is the current land use or cropping regime? (e.g., monoculture cereal, rotational grazing, orchard, or fallow land)."
            )

        if "region" not in known_variables:
            missing_labels.append("Geographic region or coordinates")
            clarifying_questions.append(
                "What region or eco-zone is the land situated in? (e.g., semi-arid Mediterranean, tropical savanna, temperate plain, or provide latitude/longitude)."
            )

        # Minimum sufficiency: At least 3 variables are present
        # (e.g. soil SOC + rainfall + crop type, or land use + pollution + biodiversity)
        is_minimally_sufficient = len(set(known_variables)) >= 3

        return is_minimally_sufficient, missing_labels, clarifying_questions


clarification_service = ClarificationService()
