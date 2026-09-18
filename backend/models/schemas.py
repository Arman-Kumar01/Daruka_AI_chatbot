from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SoilData(BaseModel):
    ph: Optional[float] = Field(None, description="Soil pH value (typically 3.5 - 9.5)")
    organic_carbon_percent: Optional[float] = Field(None, description="Soil Organic Carbon (SOC) percentage")
    moisture_percent: Optional[float] = Field(None, description="Volumetric soil moisture percentage")


class BiodiversityData(BaseModel):
    species_richness: Optional[str] = Field(None, description="Species richness assessment (low, medium, high)")
    habitat_diversity: Optional[str] = Field(None, description="Habitat structural diversity (low, medium, high)")
    pollinator_presence: Optional[str] = Field(None, description="Pollinator presence/diversity (low, medium, high)")


class HumanImpactData(BaseModel):
    pollution: Optional[str] = Field(None, description="Chemical or nutrient pollution level (low, medium, high)")
    deforestation: Optional[str] = Field(None, description="Deforestation or land clearing pressure (low, medium, high)")
    pesticide_intensity: Optional[str] = Field(None, description="Pesticide/herbicide intensity (low, medium, high)")


class GeoCoordinates(BaseModel):
    latitude: Optional[float] = Field(None, description="Latitude coordinate in degrees")
    longitude: Optional[float] = Field(None, description="Longitude coordinate in degrees")


class EnvironmentalInput(BaseModel):
    region: Optional[str] = Field(None, description="Geographic or climatic region (e.g. semi-arid, Mediterranean, tropical)")
    coordinates: Optional[GeoCoordinates] = Field(None, description="Optional latitude and longitude coordinates")
    soil: Optional[SoilData] = Field(default_factory=SoilData, description="Soil health metrics")
    land_use: Optional[str] = Field(None, description="Current land use (e.g. monoculture wheat, pasture, degraded arable)")
    rainfall: Optional[str] = Field(None, description="Rainfall pattern (e.g. low, medium, high, 350mm/yr)")
    temperature_c: Optional[float] = Field(None, description="Average ambient or seasonal temperature in Celsius")
    biodiversity: Optional[BiodiversityData] = Field(default_factory=BiodiversityData, description="Biodiversity status indicators")
    human_impact: Optional[HumanImpactData] = Field(default_factory=HumanImpactData, description="Anthropogenic pressure indicators")
    raw_query: Optional[str] = Field(None, description="Original natural language query if submitted via chat")


class EvidenceCitation(BaseModel):
    title: str
    organization: str
    year: int
    url: Optional[str] = None
    finding: str
    quantitative_metric: Optional[str] = None


class RecommendationItem(BaseModel):
    action: str
    why: str
    scientific_mechanism: str
    impacted_metrics: List[str]
    expected_change: str
    time_horizon: str  # Short term (1-2 yrs), Medium term (2-5 yrs), Long term (5-10 yrs)
    confidence: str
    interacting_variables: List[str]
    evidence: List[EvidenceCitation]


class EnvironmentalAssessment(BaseModel):
    soil: Dict[str, Any]
    climate: Dict[str, Any]
    land_use: Dict[str, Any]
    biodiversity: Dict[str, Any]
    human_impact: Dict[str, Any]


class StructuredResponse(BaseModel):
    status: str = "success"
    session_id: str
    environmental_assessment: EnvironmentalAssessment
    key_interactions: List[str]
    recommendations: List[RecommendationItem]
    evidence: List[EvidenceCitation]
    missing_information: Optional[List[str]] = None
    clarifying_questions: Optional[List[str]] = None
    scientific_summary: str
    retrieval_metadata: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: Optional[str] = None
    structured_input: Optional[EnvironmentalInput] = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    organization: str
    year: int
    url: str
    topic: str
    text: str
    score: float
    variables: List[str]


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 4
    variables_filter: Optional[List[str]] = None


class RetrieveResponse(BaseModel):
    query: str
    chunks: List[RetrievedChunk]
    total_retrieved: int
