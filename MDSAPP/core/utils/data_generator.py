# MDSAPP/core/utils/data_generator.py

import logging
import json
from typing import Dict, Any, Tuple

from google.generativeai import GenerativeModel

from MDSAPP.core.models.dossier import Klantdossier
from MDSAPP.core.utils.llm_parser import parse_llm_json_output

logger = logging.getLogger(__name__)

def _get_mock_cbs_data(region: str, period: str) -> Tuple[str, str]:
    """Simulates fetching household data from CBS."""
    source = f"CBS StatLine, {period}"
    data = f"- Gemiddelde gezinssamenstelling in {region}: 2.3 personen.\n"
    data += f"- Meest voorkomende inkomenscategorie: Modaal tot 1.5x modaal."
    logger.info(f"Mock CBS data generated for {region}")
    return data, source

def _get_mock_kadaster_data(region: str, period: str) -> Tuple[str, str]:
    """Simulates fetching sales data from Kadaster."""
    source = f"Kadaster, {period}"
    data = f"- Gemiddelde transactieprijs in {region}: 425,000 EUR.\n"
    data += f"- Meest verkochte woningtype: Rijtjeshuis."
    logger.info(f"Mock Kadaster data generated for {region}")
    return data, source

async def generate_real_estate_dossier(
    region: str, 
    budget: int, 
    llm_model: GenerativeModel
) -> Dict[str, Any]:
    """
    Generates a realistic, synthetic real estate customer dossier by first
    grounding an LLM with specific, sourced (mock) data.
    """
    logger.info(f"Starting Sourced Dossier generation for region: {region}, budget: {budget}")

    # 1. Grounding: Get data from authoritative sources (mocked)
    cbs_context, cbs_source = _get_mock_cbs_data(region, "Q1 2025")
    kadaster_context, kadaster_source = _get_mock_kadaster_data(region, "Q4 2024")
    
    grounding_context = (
        f"**Bron: {cbs_source}**\n{cbs_context}\n\n"
        f"**Bron: {kadaster_source}**\n{kadaster_context}"
    )
    sources = [cbs_source, kadaster_source]

    # 2. Construct the generator prompt
    dossier_schema = json.dumps(Klantdossier.model_json_schema(), indent=2)

    prompt = (
        f"Je bent een data generator voor een makelaarskantoor in Nederland.\n"
        f"Jouw taak is om een realistisch, fictief klantdossier te genereren.\n\n"
        f"**Stap 1: Gebruik de volgende data van gezaghebbende bronnen om je antwoord te baseren:**\n"
        f"--- START CONTEXT ---\n{grounding_context}\n--- EIND CONTEXT ---\n\n"
        f"**Stap 2: Genereer een dossier voor een klant die zoekt in de regio '{region}' met een budget van circa {budget} euro.**\n\n"
        f"**Stap 3: De output moet ENKEL een valide JSON-object zijn dat voldoet aan het volgende Pydantic-schema. Voeg geen extra tekst of markdown toe.**\n"
        f"--- START SCHEMA ---\n{dossier_schema}\n--- EIND SCHEMA ---"
    )

    # 3. Call the LLM for JSON generation
    response = await llm_model.generate_content_async(
        [prompt],
        generation_config={"response_mime_type": "application/json"}
    )
    json_string = response.candidates[0].content.parts[0].text

    # 4. Parse, validate, and self-correct the output
    validated_data = await parse_llm_json_output(json_string, Klantdossier, llm_model)

    # 5. Inject the sources into the final object
    validated_data["bronnen"] = sources
    
    return validated_data