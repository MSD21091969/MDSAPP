# MDSAPP/CasefileManagement/models/research_result.py

import uuid
import datetime
from datetime import timezone
from typing import List, Dict, Any

from pydantic import BaseModel, Field

class SourceDocument(BaseModel):
    """
    Represents a source document used for research or RAG.
    """
    document_id: str
    source: str  # e.g., 'Google Drive', 'Web Search', 'Database'
    content_fragment: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ResearchResult(BaseModel):
    """
    Represents the result of a data research task, created by the EngineerAgent.
    """
    result_id: str = Field(default_factory=lambda: f"res-research-{uuid.uuid4().hex[:10]}")
    query: str
    summary: str
    source_documents: List[SourceDocument] = Field(default_factory=list)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(timezone.utc))
