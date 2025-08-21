from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Mission(BaseModel):
    """
    Defines the structured mission for a workflow, including its goal and specific parameters.
    """
    goal: str = Field(..., description="The primary objective or desired outcome of the mission.")
    context: str = Field(..., description="The general context or scenario for the mission (e.g., 'real estate market analysis').")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of specific parameters for the mission (e.g., 'location', 'income_data', 'property_value_range').")
    constraints: Optional[str] = Field(None, description="Any specific limitations or constraints for the mission.")
    target_audience: Optional[str] = Field(None, description="The intended audience for the mission's outcome (e.g., 'real estate agent', 'investors').")
    timeframe: Optional[str] = Field(None, description="The desired timeframe for the mission's completion (e.g., '2024 Q4').")
