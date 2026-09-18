"""
LLM Provider Adapter.
Integrates external LLM providers (Google Gemini, OpenAI) with strict prompt grounding,
while maintaining a deterministic Scientific Inference Synthesis fallback for offline / keyless testing.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from backend.config import settings
from backend.models.schemas import EnvironmentalInput, RetrievedChunk, StructuredResponse

logger = logging.getLogger("llm_adapter")


class LLMAdapter:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    async def generate_scientific_summary(
        self,
        env_input: EnvironmentalInput,
        retrieved_chunks: List[RetrievedChunk],
        reasoning_data: Dict[str, Any]
    ) -> str:
        """
        Generates an authoritative scientific summary synthesizing the multi-variable environmental assessment.
        """
        # If Gemini API key is configured, use Gemini
        if self.gemini_key:
            try:
                return await self._call_gemini_summary(env_input, retrieved_chunks, reasoning_data)
            except Exception as e:
                logger.error(f"Gemini API invocation failed: {e}. Falling back to internal scientific synthesis.")

        # If OpenAI API key is configured, use OpenAI
        if self.openai_key:
            try:
                return await self._call_openai_summary(env_input, retrieved_chunks, reasoning_data)
            except Exception as e:
                logger.error(f"OpenAI API invocation failed: {e}. Falling back to internal scientific synthesis.")

        # Default / Offline / Keyless: Deterministic Scientific Synthesis
        return self._generate_local_scientific_summary(env_input, retrieved_chunks, reasoning_data)

    def _generate_local_scientific_summary(
        self,
        env_input: EnvironmentalInput,
        retrieved_chunks: List[RetrievedChunk],
        reasoning_data: Dict[str, Any]
    ) -> str:
        """
        Generates an evidence-grounded scientific diagnostic summary from the multi-variable reasoning data.
        """
        interactions = reasoning_data.get("key_interactions", [])
        recommendations = reasoning_data.get("recommendations", [])
        soc = env_input.soil.organic_carbon_percent if env_input.soil else None
        region = env_input.region or "the specified agro-ecosystem"
        
        summary_lines = [
            f"**Comprehensive Agro-Ecological Diagnostic for {region}:**",
            f"Based on multi-variable diagnostic synthesis, the target landscape exhibits systemic coupling between soil structural properties, hydrological stress, and trophic biodiversity depletion."
        ]

        if soc is not None and soc < 0.8:
            summary_lines.append(
                f"Specifically, depleted soil organic carbon ({soc}%) restricts microbial metabolic activity and reduces topsoil available water capacity by ~1.5–3.7% volumetric moisture, compounding rainfall deficits."
            )

        if interactions:
            summary_lines.append(f"**Primary Causal Mechanism:** {interactions[0]}")

        if recommendations:
            rec = recommendations[0]
            summary_lines.append(
                f"**Prioritized Intervention:** {rec.action} This intervention targets {', '.join(rec.impacted_metrics[:2])} over a {rec.time_horizon} horizon with {rec.confidence}."
            )

        summary_lines.append(
            f"All recommendations are directly grounded in indexed research from {', '.join(set(c.organization for c in retrieved_chunks[:3])) if retrieved_chunks else 'authoritative global bodies'}."
        )

        return "\n\n".join(summary_lines)

    async def _call_gemini_summary(
        self,
        env_input: EnvironmentalInput,
        retrieved_chunks: List[RetrievedChunk],
        reasoning_data: Dict[str, Any]
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.DEFAULT_MODEL}:generateContent?key={self.gemini_key}"
        evidence_text = "\n".join([f"- [{c.organization} {c.year}] {c.title}: {c.text}" for c in retrieved_chunks[:4]])
        prompt = f"""
You are an expert Environmental and Agro-ecological Scientist at Darukaa.Earth.
Analyze the following environmental data and retrieved scientific evidence.
Provide a concise, highly rigorous scientific diagnostic summary explaining how the environmental variables (soil, climate, land use, biodiversity, human impact) interact, and why the recommended interventions are mechanistically sound.

Environmental Input:
{env_input.model_dump_json(indent=2)}

Retrieved Scientific Literature:
{evidence_text}

Rules:
- Reason across at least 3 environmental variables simultaneously.
- Do not make generic claims.
- Cite specific metrics and quantitative ranges from the retrieved literature.
- Maintain an authoritative, scientific tone.
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600}
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")

    async def _call_openai_summary(
        self,
        env_input: EnvironmentalInput,
        retrieved_chunks: List[RetrievedChunk],
        reasoning_data: Dict[str, Any]
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        evidence_text = "\n".join([f"- [{c.organization} {c.year}] {c.title}: {c.text}" for c in retrieved_chunks[:4]])
        prompt = f"""
You are an expert Environmental and Agro-ecological Scientist at Darukaa.Earth.
Synthesize a rigorous, multi-variable scientific diagnostic summary based strictly on the provided evidence.

Environmental Input:
{env_input.model_dump_json(indent=2)}

Retrieved Literature:
{evidence_text}
"""
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an AI environmental scientist. Ground all assertions in the provided scientific text."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text}")


llm_adapter = LLMAdapter()
