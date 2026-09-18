"""
Geo-spatial Biome & Spatial Context Resolver.
Maps latitude / longitude coordinates and regional descriptors to ecological biomes,
typical soil regimes, and climate baselines without external paid APIs.
"""

from typing import Dict, Any, Optional
from backend.models.schemas import GeoCoordinates


def resolve_spatial_context(
    coords: Optional[GeoCoordinates] = None,
    region_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Infers eco-region, biome category, and baseline ecological stressors
    based on geographic coordinates or region keywords.
    """
    inferred_biome = "Temperate agro-ecosystem"
    climate_zone = "Sub-humid"
    primary_stressors = ["Nutrient runoff", "Habitat fragmentation"]
    soil_vulnerability = "Moderate erosion vulnerability"

    # 1. Coordinate-based rule resolution (Offline GIS approximation)
    if coords and coords.latitude is not None and coords.longitude is not None:
        lat = coords.latitude
        lon = coords.longitude
        abs_lat = abs(lat)

        if abs_lat <= 15:
            inferred_biome = "Tropical Humid / Sub-humid Agro-ecosystem"
            climate_zone = "Tropical"
            primary_stressors = ["Rapid organic matter oxidation", "Phosphorus fixation", "Deforestation"]
            soil_vulnerability = "High leaching and acidification risk (Oxisols/Ultisols)"
        elif 15 < abs_lat <= 35:
            # Check for Mediterranean or Arid zones
            if (lon >= -10 and lon <= 40 and 30 <= lat <= 45) or (lon >= -125 and lon <= -115 and 30 <= lat <= 38):
                inferred_biome = "Mediterranean Dryland & Scrubland"
                climate_zone = "Semi-arid Mediterranean"
                primary_stressors = ["Summer drought", "Low soil moisture", "Wildfire risk"]
                soil_vulnerability = "Calcareous topsoil, low organic carbon"
            else:
                inferred_biome = "Subtropical Dryland / Semi-arid Zone"
                climate_zone = "Semi-arid"
                primary_stressors = ["Water scarcity", "Thermal stress", "Wind erosion"]
                soil_vulnerability = "Aridisol degradation, high salinization risk"
        elif 35 < abs_lat <= 55:
            inferred_biome = "Temperate Mixed Cropland & Forest Steppe"
            climate_zone = "Temperate"
            primary_stressors = ["Intensive tillage compaction", "Pesticide accumulation", "Biodiversity corridor loss"]
            soil_vulnerability = "Topsoil loss under continuous monoculture"
        else:
            inferred_biome = "Boreal / High-Latitude Agro-pastoral"
            climate_zone = "Cold Continental"
            primary_stressors = ["Short growing season", "Waterlogging during spring thaw"]
            soil_vulnerability = "Slow organic matter mineralization"

    # 2. Refine or override if explicit region name is given
    if region_name:
        r_lower = region_name.lower()
        if "semi-arid" in r_lower or "dryland" in r_lower or "arid" in r_lower:
            inferred_biome = "Semi-arid Dryland Agroecosystem"
            climate_zone = "Semi-arid"
            primary_stressors = ["Moisture deficit", "Rapid organic matter depletion", "Wind erosion"]
            soil_vulnerability = "Low SOC (<0.8%), high crusting tendency"
        elif "tropical" in r_lower or "rainforest" in r_lower:
            inferred_biome = "Tropical Agroforestry / Plantation Landscape"
            climate_zone = "Humid Tropical"
            primary_stressors = ["Heavy nutrient leaching", "Deforestation pressure"]
        elif "mediterranean" in r_lower:
            inferred_biome = "Mediterranean Basin Agro-ecosystem"
            climate_zone = "Mediterranean"
            primary_stressors = ["Seasonal drought", "Summer heatwaves"]
        elif "floodplain" in r_lower or "wetland" in r_lower or "lowland" in r_lower:
            inferred_biome = "Lowland Riparian / Floodplain Agricultural Basin"
            climate_zone = "Hydric / Sub-humid"
            primary_stressors = ["Seasonal waterlogging", "Agrochemical runoff", "Eutrophication"]

    return {
        "inferred_biome": inferred_biome,
        "climate_zone": climate_zone,
        "primary_stressors": primary_stressors,
        "soil_vulnerability": soil_vulnerability,
        "latitude": coords.latitude if coords else None,
        "longitude": coords.longitude if coords else None
    }
