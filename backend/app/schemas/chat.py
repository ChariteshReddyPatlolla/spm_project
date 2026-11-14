from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Citation(BaseModel):
    paper_title: str
    page_number: int
    document_id: str
    snippet: str
    relevance_score: Optional[float] = None
    is_validated: bool = True

class AgentStep(BaseModel):
    step_name: str
    description: str
    status: str = "completed"
    details: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    selected_document_ids: Optional[List[str]] = Field(default_factory=list)
    use_agentic_workflow: bool = True

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: List[Citation] = Field(default_factory=list)
    agent_steps: List[AgentStep] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    title: Optional[str] = "New Research Session"
    topic: Optional[str] = "General Research"
    selected_document_ids: Optional[List[str]] = Field(default_factory=list)

class SessionResponse(BaseModel):
    id: str
    title: str
    topic: str
    selected_document_ids: List[str]
    rolling_summary: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
