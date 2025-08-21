# MDSAPP/core/models/ontology.py
from enum import Enum

class CasefileType(str, Enum):
    """
    Defines the high-level types of casefiles.
    """
    ERBAN = "erban"
    RESEARCH = "research"

class WorkflowType(str, Enum):
    """
    Defines the types of workflows.
    """
    ANALYSIS = "analysis"
    EXECUTION = "execution"

class ElementType(str, Enum):
    """
    Defines the types of elements that can be part of a workflow.
    """
    AI_AGENT = "ai_agent"
    TOOL = "tool"
    HUMAN = "human"

class WorkflowExecutionMode(str, Enum):
    """
    Defines how the elements in a workflow are executed.
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"

class WorkflowStatus(str, Enum):
    """
    Defines the possible statuses of a workflow execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(str, Enum):
    """
    Defines the possible statuses of a step execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class EventType(str, Enum):
    """
    Defines the single source of truth for all event types in the system's 'tickertape'.
    """
    # --- Gebruiker & Agent Interactie ---
    USER_MESSAGE = "USER_MESSAGE"      # Een bericht direct van de gebruiker.
    AGENT_MESSAGE = "AGENT_MESSAGE"    # Een antwoord van een agent aan de gebruiker.
    AGENT_THOUGHT = "AGENT_THOUGHT"    # De interne redenering van een agent.

    # --- Tool & Actie Uitvoering ---
    TOOL_CALL = "TOOL_CALL"            # Een agent roept een tool aan.
    TOOL_RESULT = "TOOL_RESULT"        # Een tool geeft een resultaat terug.
    
    # --- Taak & Planning Levenscyclus ---
    TASK_PLANNED = "TASK_PLANNED"      # Een taak is ingepland voor de toekomst.
    TASK_STARTED = "TASK_STARTED"      # De scheduler pakt een geplande taak op.
    TASK_COMPLETED = "TASK_COMPLETED"  # Een taak is succesvol afgerond.
    TASK_FAILED = "TASK_FAILED"        # Een taak is mislukt.
    
    # --- Object & Systeem Levenscyclus ---
    OBJECT_CREATED = "OBJECT_CREATED"  # Een object (Casefile, Workflow) is aangemaakt.
    OBJECT_UPDATED = "OBJECT_UPDATED"  # Een object is bijgewerkt.
    SYSTEM_LOG = "SYSTEM_LOG"          # Een generiek systeem-logbericht.

class EventStatus(str, Enum): # Added EventStatus
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    LOGGED = "LOGGED"

class Role(str, Enum):
    """
    Defines the access control roles for a casefile.
    """
    ADMIN = "admin"
    WRITER = "writer"
    READER = "reader"
