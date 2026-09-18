"""
Conversation & State Accumulation Manager.
Maintains multi-turn conversation memory, extracts environmental variables from natural language text,
and merges partial inputs into a cumulative environmental state.
"""

import re
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

from backend.models.schemas import (
    EnvironmentalInput,
    SoilData,
    BiodiversityData,
    HumanImpactData,
    GeoCoordinates,
    ChatMessage
)
from backend.services.clarification_service import clarification_service


class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.messages: List[ChatMessage] = []
        self.cumulative_state: EnvironmentalInput = EnvironmentalInput()

    def add_message(self, role: str, content: str):
        self.messages.append(
            ChatMessage(
                role=role,
                content=content,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        )

    def merge_input(self, new_input: EnvironmentalInput):
        """Merges new environmental input into cumulative session state without overwriting existing known data unless specified."""
        if new_input.region:
            self.cumulative_state.region = new_input.region

        if new_input.coordinates:
            if not self.cumulative_state.coordinates:
                self.cumulative_state.coordinates = GeoCoordinates()
            if new_input.coordinates.latitude is not None:
                self.cumulative_state.coordinates.latitude = new_input.coordinates.latitude
            if new_input.coordinates.longitude is not None:
                self.cumulative_state.coordinates.longitude = new_input.coordinates.longitude

        if new_input.land_use:
            self.cumulative_state.land_use = new_input.land_use

        if new_input.rainfall:
            self.cumulative_state.rainfall = new_input.rainfall

        if new_input.temperature_c is not None:
            self.cumulative_state.temperature_c = new_input.temperature_c

        # Soil merge
        if new_input.soil:
            if not self.cumulative_state.soil:
                self.cumulative_state.soil = SoilData()
            if new_input.soil.ph is not None:
                self.cumulative_state.soil.ph = new_input.soil.ph
            if new_input.soil.organic_carbon_percent is not None:
                self.cumulative_state.soil.organic_carbon_percent = new_input.soil.organic_carbon_percent
            if new_input.soil.moisture_percent is not None:
                self.cumulative_state.soil.moisture_percent = new_input.soil.moisture_percent

        # Biodiversity merge
        if new_input.biodiversity:
            if not self.cumulative_state.biodiversity:
                self.cumulative_state.biodiversity = BiodiversityData()
            if new_input.biodiversity.species_richness:
                self.cumulative_state.biodiversity.species_richness = new_input.biodiversity.species_richness
            if new_input.biodiversity.habitat_diversity:
                self.cumulative_state.biodiversity.habitat_diversity = new_input.biodiversity.habitat_diversity
            if new_input.biodiversity.pollinator_presence:
                self.cumulative_state.biodiversity.pollinator_presence = new_input.biodiversity.pollinator_presence

        # Human impact merge
        if new_input.human_impact:
            if not self.cumulative_state.human_impact:
                self.cumulative_state.human_impact = HumanImpactData()
            if new_input.human_impact.pollution:
                self.cumulative_state.human_impact.pollution = new_input.human_impact.pollution
            if new_input.human_impact.deforestation:
                self.cumulative_state.human_impact.deforestation = new_input.human_impact.deforestation
            if new_input.human_impact.pesticide_intensity:
                self.cumulative_state.human_impact.pesticide_intensity = new_input.human_impact.pesticide_intensity


class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = ConversationSession(new_id)
            return self.sessions[new_id]
        return self.sessions[session_id]

    def parse_natural_language(self, text: str) -> EnvironmentalInput:
        """
        Extracts structured environmental metrics from free-form text using regex and keyword heuristics.
        """
        extracted = EnvironmentalInput(raw_query=text)
        soil = SoilData()
        bio = BiodiversityData()
        human = HumanImpactData()
        coords = GeoCoordinates()

        # Soil Organic Carbon % extraction (e.g., "SOC 0.3%", "organic carbon: 0.3%", "carbon is 0.4")
        soc_match = re.search(r'(?:soil\s+organic\s+carbon|soc|organic\s+carbon)\s*(?:is|:|=)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?', text, re.IGNORECASE)
        if soc_match:
            try:
                soil.organic_carbon_percent = float(soc_match.group(1))
            except ValueError:
                pass

        # Soil pH extraction (e.g., "pH 6.2", "pH is 5.8", "pH: 7.1")
        ph_match = re.search(r'\bph\s*(?:is|:|=)?\s*([0-9]+(?:\.[0-9]+)?)\b', text, re.IGNORECASE)
        if ph_match:
            try:
                val = float(ph_match.group(1))
                if 2.0 <= val <= 12.0:
                    soil.ph = val
            except ValueError:
                pass

        # Soil moisture % extraction (e.g. "moisture 12%", "soil moisture: 15%")
        moisture_match = re.search(r'(?:soil\s+)?moisture\s*(?:is|:|=)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?', text, re.IGNORECASE)
        if moisture_match:
            try:
                soil.moisture_percent = float(moisture_match.group(1))
            except ValueError:
                pass

        # Rainfall extraction (e.g. "rainfall: low", "low rainfall", "rainfall is high", "rainfall 300mm")
        if re.search(r'\b(low\s+rainfall|rainfall\s*(?:is|:)?\s*low|scant\s+rainfall|drought)\b', text, re.IGNORECASE):
            extracted.rainfall = "low"
        elif re.search(r'\b(high\s+rainfall|rainfall\s*(?:is|:)?\s*high|heavy\s+rainfall)\b', text, re.IGNORECASE):
            extracted.rainfall = "high"
        elif re.search(r'\b(moderate\s+rainfall|rainfall\s*(?:is|:)?\s*medium)\b', text, re.IGNORECASE):
            extracted.rainfall = "medium"

        # Temperature extraction (e.g. "31°C", "31 C", "temperature 31", "temperature is 28 degrees")
        temp_match = re.search(r'(?:temperature|temp)\s*(?:is|:|=)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:°?C|deg|degrees)?', text, re.IGNORECASE)
        if not temp_match:
            temp_match = re.search(r'\b([0-9]{1,2}(?:\.[0-9]+)?)\s*°C\b', text, re.IGNORECASE)
        if temp_match:
            try:
                extracted.temperature_c = float(temp_match.group(1))
            except ValueError:
                pass

        # Land use extraction (e.g. "monoculture wheat", "wheat", "pasture", "agroforestry")
        land_match = re.search(r'(?:crop|land[\s-]use)\s*(?:is|:|=)?\s*([a-zA-Z0-9\s\-]+?)(?:[,.]|$)', text, re.IGNORECASE)
        if land_match:
            extracted.land_use = land_match.group(1).strip()
        elif re.search(r'\b(monoculture\s+wheat|wheat\s+monoculture)\b', text, re.IGNORECASE):
            extracted.land_use = "monoculture wheat"
        elif "monoculture" in text.lower():
            extracted.land_use = "monoculture"

        # Region extraction (e.g. "semi-arid", "arid", "mediterranean", "tropical")
        if re.search(r'\bsemi[\s-]arid\b', text, re.IGNORECASE):
            extracted.region = "semi-arid"
        elif re.search(r'\bmediterranean\b', text, re.IGNORECASE):
            extracted.region = "Mediterranean"
        elif re.search(r'\btropical\b', text, re.IGNORECASE):
            extracted.region = "tropical"
        elif re.search(r'\btemperate\b', text, re.IGNORECASE):
            extracted.region = "temperate"

        # Biodiversity extraction
        if re.search(r'\b(?:declining\s+biodiversity|biodiversity\s+is\s+declining|low\s+species\s+richness|species\s+richness\s*(?:is|:)?\s*low|biodiversity\s+loss)\b', text, re.IGNORECASE):
            bio.species_richness = "low"
        if re.search(r'(?:habitat\s+diversity\s*(?:is|:)?\s*low|fragmentation|isolated\s+patches)', text, re.IGNORECASE):
            bio.habitat_diversity = "low (fragmented)"

        # Human Impact / Pollution
        if re.search(r'(?:pollution\s*(?:is|:)?\s*high|high\s+pollution|chemical\s+runoff|heavy\s+pesticides)', text, re.IGNORECASE):
            human.pollution = "high"
        elif re.search(r'(?:pollution\s*(?:is|:)?\s*medium|moderate\s+pollution)', text, re.IGNORECASE):
            human.pollution = "medium"

        if re.search(r'(?:deforestation\s*(?:is|:)?\s*high|heavy\s+clearing)', text, re.IGNORECASE):
            human.deforestation = "high"
        elif re.search(r'(?:deforestation\s*(?:is|:)?\s*low|minimal\s+clearing)', text, re.IGNORECASE):
            human.deforestation = "low"

        # Coordinates (e.g. "lat: 31.5, lon: 35.2")
        coord_match = re.search(r'lat(?:itude)?\s*[:=]?\s*([+-]?[0-9]+(?:\.[0-9]+)?)[,\s]+lon(?:gitude)?\s*[:=]?\s*([+-]?[0-9]+(?:\.[0-9]+)?)', text, re.IGNORECASE)
        if coord_match:
            try:
                coords.latitude = float(coord_match.group(1))
                coords.longitude = float(coord_match.group(2))
            except ValueError:
                pass

        if soil.ph is not None or soil.organic_carbon_percent is not None or soil.moisture_percent is not None:
            extracted.soil = soil
        else:
            extracted.soil = None

        if bio.species_richness is not None or bio.habitat_diversity is not None or bio.pollinator_presence is not None:
            extracted.biodiversity = bio
        else:
            extracted.biodiversity = None

        if human.pollution is not None or human.deforestation is not None or human.pesticide_intensity is not None:
            extracted.human_impact = human
        else:
            extracted.human_impact = None

        if coords.latitude is not None:
            extracted.coordinates = coords
        else:
            extracted.coordinates = None

        return extracted


conversation_manager = ConversationManager()
