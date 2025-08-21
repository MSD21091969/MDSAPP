# MDSAPP/core/models/conversation_session.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Message(BaseModel):
    role: str
    content: str

class ConversationSession(BaseModel):
    """
    Represents the state of a single conversation session.
    """
    id: str = Field(..., description="Unique identifier for the conversation session.")
    casefile_id: Optional[str] = Field(None, description="ID of the associated casefile, if any.")
    history: List[Message] = Field(default_factory=list, description="List of messages in the conversation.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the session.")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv-12345",
                "casefile_id": "case-abcde",
                "history": [
                    {"role": "user", "content": "Hello, how can I help you?"},
                    {"role": "model", "content": "I need assistance with my casefile."}
                ],
                "metadata": {
                    "start_time": "2025-08-21T10:00:00Z",
                    "user_id": "user-xyz"
                }
            }
        }
