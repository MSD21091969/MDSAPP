# MDSAPP/WorkFlowManagement/models/results.py

import uuid
import datetime
from datetime import timezone
from typing import List, Dict, Any

from pydantic import BaseModel, Field

# Updated import
from MDSAPP.core.models.ontology import WorkflowStatus, StepStatus

class StepResult(BaseModel):
    """
    Represents the result of a single step (Element) in a workflow execution.
    """
    element_id: str
    status: StepStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime.datetime
    ended_at: datetime.datetime

class WorkflowExecutionResult(BaseModel):
    """
    Represents the final result of a complete workflow execution.
    This object will be nested within a Casefile.
    """
    result_id: str = Field(default_factory=lambda: f"res-{uuid.uuid4().hex[:10]}")
    workflow_id: str
    status: WorkflowStatus
    steps: List[StepResult]
    started_at: datetime.datetime
    ended_at: datetime.datetime


