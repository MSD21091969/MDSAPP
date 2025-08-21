from pydantic import BaseModel
from typing import Any, Dict, Optional
from enum import Enum

# Import Casefile related models for command parameters
from MDSAPP.CasefileManagement.models.casefile import Casefile, Event
from MDSAPP.core.models.stix_inspired_models import Campaign, Grouping

class CommandStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    DISPATCHED = "DISPATCHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Command(BaseModel):
    command_id: str # Unique ID for the command
    command_type: str # e.g., "CREATE_CASEFILE", "UPDATE_CASEFILE"
    source_agent: str # The agent that issued the command
    user_id: str # The ID of the user who initiated the command
    timestamp: str # ISO format timestamp
    payload: Dict[str, Any] # The actual data/parameters for the command
    status: CommandStatus = CommandStatus.RECEIVED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CreateCasefileCommand(Command):
    command_type: str = "CREATE_CASEFILE"
    payload: Dict[str, Any] # Overriding payload to be more specific if needed, or keep generic

class UpdateCasefileCommand(Command):
    command_type: str = "UPDATE_CASEFILE"
    payload: Dict[str, Any] # Must contain casefile_id and updates

class DeleteCasefileCommand(Command):
    command_type: str = "DELETE_CASEFILE"
    payload: Dict[str, Any] # Must contain casefile_id

class LogEventCommand(Command):
    command_type: str = "LOG_EVENT"
    payload: Dict[str, Any] # Must contain casefile_id, source, event_type, content, metadata

class GetCasefileCommand(Command):
    command_type: str = "GET_CASEFILE"
    payload: Dict[str, Any] # Must contain casefile_id

class ListAllCasefilesCommand(Command):
    command_type: str = "LIST_ALL_CASEFILES"
    payload: Dict[str, Any] # No specific payload needed, but keep for consistency

class RunEngineerAgentCommand(Command):
    command_type: str = "RUN_ENGINEER_AGENT"
    payload: Dict[str, Any] # Must contain the query for the engineer agent

# Add more specific command models as needed for other managers
