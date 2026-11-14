from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.chat import Citation

class SummaryRequest(BaseModel):
    document_id: str
    regenerate: bool = False

class PaperSummaryResponse(BaseModel):
    id: str
    document_id: str
    title: str
    authors: str
    research_objective: str
    problem_statement: str
    methodology: str
    proposed_architecture: str
    algorithms_and_models: str
    datasets: str
    evaluation_metrics: str
    experimental_results: str
    main_contributions: str
    limitations: str
    future_research_directions: str
    citations: List[Citation] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
