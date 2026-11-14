from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.chat import Citation

class ComparisonRow(BaseModel):
    aspect: str
    values: Dict[str, str]  # paper_id or title -> value

class AdvantageDisadvantage(BaseModel):
    paper_title: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)

class ComparativeAnalysisRequest(BaseModel):
    document_ids: List[str]
    custom_aspects: Optional[List[str]] = None

class ComparativeAnalysisResponse(BaseModel):
    id: str
    title: str
    document_ids: List[str]
    paper_titles: Dict[str, str]  # id -> title
    comparison_table: List[ComparisonRow]
    detailed_analysis: str
    advantages_disadvantages: List[AdvantageDisadvantage]
    research_gaps: str
    citations: List[Citation] = Field(default_factory=list)
    created_at: datetime

