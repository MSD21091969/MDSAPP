from pydantic import BaseModel, Field
import datetime
import uuid

class Prompt(BaseModel):
    """A model for storing and versioning prompts."""
    id: str = Field(default_factory=lambda: f"prompt-{uuid.uuid4().hex[:10]}")
    agent_name: str
    task_name: str
    version: int = 1
    template: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    def touch(self):
        """Updates the 'updated_at' timestamp to the current time."""
        self.updated_at = datetime.datetime.utcnow()
