# MDSAPP/WorkFlowManagement/models/workflow.py

import uuid
from typing import List, Dict, Any, Literal

from pydantic import BaseModel, Field

# Updated import
from MDSAPP.core.models.ontology import WorkflowType, ElementType

class Element(BaseModel):
    """
    Represents a single unit of work in a workflow (e.g., an AI agent, a tool, or a human).
    """
    id: str = Field(default_factory=lambda: f"el-{uuid.uuid4().hex[:10]}")
    name: str
    type: ElementType
    instruction: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class WorkflowNode(BaseModel):
    """
    Represents a node in the workflow graph, which corresponds to an Element.
    """
    element_id: str

class WorkflowCondition(BaseModel):
    target_node_id: str
    condition_type: str
    condition: Dict[str, Any]

class WorkflowEdge(BaseModel):
    """
    Represents a directed edge between two nodes in the workflow graph.
    """
    source_node_id: str
    conditions: List[WorkflowCondition]

class WorkflowDynamics(BaseModel):
    """
    Represents the structure and logic of a workflow as a Directed Acyclic Graph (DAG).
    This is the crucial "ADK link" that defines how the workflow is executed.
    """
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    start_node_id: str

class Workflow(BaseModel):
    """
    Represents a specific, executable instance of a workflow, nested within a Casefile.
    """
    workflow_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:10]}")
    type: WorkflowType = WorkflowType.ANALYSIS
    elements: List[Element]
    dynamics: WorkflowDynamics
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EngineeredWorkflow(Workflow):
    """
    Represents a structured, reusable workflow template.
    """
    engineered_workflow_id: str = Field(default_factory=lambda: f"eng-wf-{uuid.uuid4().hex[:10]}")
    name: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)