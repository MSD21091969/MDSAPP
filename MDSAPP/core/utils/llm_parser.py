# MDSAPP/core/utils/llm_parser.py

import logging
import json
import re  # Importeer de regex module
from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError
from google.generativeai import GenerativeModel

logger = logging.getLogger(__name__)

async def parse_llm_json_output(
    json_string: str, 
    pydantic_model: Type[BaseModel], 
    llm_model: GenerativeModel
) -> Dict[str, Any]:
    """
    Parses a JSON string from LLM output, validates it with a Pydantic model,
    and attempts to self-correct if parsing fails.
    """
    try:
        # EERSTE WIJZIGING: Extraheer JSON uit de initiële input
        match = re.search(r"```json\n(.*?)\n```", json_string, re.DOTALL)
        if match:
            clean_json_string = match.group(1).strip()
        else:
            clean_json_string = json_string.strip()

        data = json.loads(clean_json_string)
        pydantic_model(**data)
        logger.info(f"Successfully parsed and validated JSON for model {pydantic_model.__name__}.")
        return data
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"Initial JSON parsing/validation failed for {pydantic_model.__name__}: {e}. Attempting self-correction.")
        if isinstance(e, ValidationError):
            logger.warning(f"Pydantic validation errors: {e.errors()}")

        # Gebruik de originele, mogelijk 'vuile' json_string in de correctie-prompt
        error_details = e.errors() if isinstance(e, ValidationError) else str(e)
        correction_prompt = (
            f"The following JSON output is invalid. Please correct it and return only the valid JSON object. "
            f"Do not include any explanatory text or markdown. The specific errors were: {error_details}\n\n"
            f"Invalid JSON:\n```json\n{json_string}\n```")

        logger.info(f"Self-correction prompt sent to LLM...")
        response = await llm_model.generate_content_async([correction_prompt])
        corrected_json_string = response.text
        logger.info(f"Raw response from self-correction LLM: {corrected_json_string}")

        try:
            # TWEEDE WIJZIGING: Extraheer JSON ook uit de gecorrigeerde output
            final_match = re.search(r"```json\n(.*?)\n```", corrected_json_string, re.DOTALL)
            if final_match:
                final_json_string = final_match.group(1).strip()
                logger.info("Extracted JSON from self-correction response markdown block.")
            else:
                final_json_string = corrected_json_string.strip()
                logger.warning("No markdown block in self-correction response, parsing raw text.")
            
            data = json.loads(final_json_string)
            pydantic_model(**data)
            logger.info(f"Successfully parsed and validated JSON for model {pydantic_model.__name__} after self-correction.")
            return data
        except (json.JSONDecodeError, ValidationError) as final_e:
            logger.error(f"Final JSON parsing/validation failed after self-correction: {final_e}")
            raise ValueError(f"Failed to parse LLM output for {pydantic_model.__name__}, even after self-correction.") from final_e