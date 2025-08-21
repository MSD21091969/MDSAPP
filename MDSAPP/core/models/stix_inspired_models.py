# In a new file: MDSAPP/core/models/stix_inspired_models.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import datetime
import uuid

class STIXObject(BaseModel):
    """A base model for all STIX-inspired objects."""
    type: str
    spec_version: str = "2.1"
    id: Optional[str] = None # Make it optional
    created: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + 'Z')
    modified: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + 'Z')

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None: # If id was not provided or was None
            self.id = f"{self.type}--{uuid.uuid4()}"

class Identity(STIXObject):
    """Represents an individual, organization, or group."""
    type: str = "identity"
    name: str
    description: Optional[str] = None
    identity_class: str # e.g., "individual", "organization"
    roles: List[str] = Field(default_factory=list)

class Grouping(STIXObject):
    """Represents a collection of related objects, like a dossier or case."""
    type: str = "grouping"
    name: str
    description: Optional[str] = None
    context: str # e.g., "customer-dossier", "market-analysis"
    object_refs: List[str] = Field(default_factory=list) # List of IDs of other objects in this group

class Campaign(STIXObject):
    """Represents a mission or a set of goal-oriented activities."""
    type: str = "campaign"
    name: str # The goal of the mission
    description: Optional[str] = None # The context
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
