# MDSAPP/core/tools/research_tools.py

import logging
import os
import httpx
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def google_web_search(query: str) -> List[Dict[str, Any]]:
    """
    Performs a web search using the Google Custom Search API.

    Args:
        query: The search query.

    Returns:
        A list of search results.
    """
    logger.info(f"[TOOL] Performing Google web search for: {query}")

    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        logger.error("GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are not set.")
        return [{"error": "Google Search API is not configured."}]

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            search_results = response.json()
            return search_results.get("items", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"An error occurred during Google web search: {e}")
            return [{"error": f"An error occurred during Google web search: {e}"}]
