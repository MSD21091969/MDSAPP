# MDSAPP/core/tools/real_estate_tools.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_kadaster_info(adres: str) -> Dict[str, Any]:
    """
    A mock tool that simulates fetching data from the Kadaster for a given address.
    In a real implementation, this would call an external API.

    Args:
        adres: The address to look up.

    Returns:
        A dictionary with property information.
    """
    logger.info(f"[TOOL] Simulating Kadaster lookup for address: {adres}")

    # Mock database
    mock_data = {
        "Velperweg 152, 6824 HE Arnhem": {
            "oppervlakte_perceel": 220,
            "eigendomssituatie": "Volledig eigendom",
            "aankoopjaar": 2018
        }
    }

    result = mock_data.get(adres, {"error": "Adres niet gevonden in Kadaster."})
    
    return result
