# MDSAPP/CasefileManagement/models/casefile.py

import uuid
import datetime
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

from pydantic import BaseModel, Field

# Updated imports from MDSAPP/core/models/ontology
from MDSAPP.core.models.ontology import CasefileType, EventType, EventStatus, Role

# Updated imports from MDSAPP/WorkFlowManagement/models/workflow and results
from MDSAPP.WorkFlowManagement.models.workflow import Workflow, EngineeredWorkflow
from MDSAPP.WorkFlowManagement.models.results import WorkflowExecutionResult
from MDSAPP.CasefileManagement.models.research_result import ResearchResult

from MDSAPP.core.models.stix_inspired_models import Campaign, Grouping # New import

class DriveFileReference(BaseModel):
    id: str
    name: str
    mime_type: str
    web_view_link: str
    icon_link: str
    path: str

class Event(BaseModel):
    id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:10]}")
    source: Literal["USER", "CHAT_AGENT", "PROCESSOR_AGENT", "EXECUTOR_AGENT", "ENGINEER_AGENT", "SYSTEM"]
    event_type: EventType = EventType.SYSTEM_LOG
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    scheduled_time: Optional[str] = None
    status: EventStatus = EventStatus.LOGGED

class Casefile(BaseModel):
    """
    The central, all-encompassing dossier-object for the MDS platform.
    It can be nested to represent a hierarchy of casefiles.
    """
    id: Optional[str] = Field(default_factory=lambda: f"case-{uuid.uuid4().hex[:10]}")
    name: str
    description: str = ""
    casefile_type: str = "research"

    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    modified_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    owner_id: Optional[str] = None # Added Optional for now
    acl: Dict[str, Role] = Field(default_factory=dict)

    tags: List[str] = Field(default_factory=list)
    campaign: Optional[Campaign] = None # Represents the mission
    dossier: Optional[Grouping] = None # Represents the collection of related data

    sub_casefile_ids: List[str] = Field(
        default_factory=list,
        description="A list of IDs of nested sub-casefiles."
    )
    parent_id: Optional[str] = None

    workflows: List[Workflow] = Field(default_factory=list)
    engineered_workflows: List[EngineeredWorkflow] = Field(default_factory=list)
    execution_results: List[WorkflowExecutionResult] = Field(default_factory=list)
    research_results: List[ResearchResult] = Field(default_factory=list)

    file_references: List[DriveFileReference] = Field(default_factory=list)
    event_log: List[Event] = Field(default_factory=list)

    embedding: Optional[List[float]] = None

    def touch(self):
        self.modified_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

Casefile.model_rebuild()
