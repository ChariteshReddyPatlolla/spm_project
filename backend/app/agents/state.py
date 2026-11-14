from typing import List, Dict, Any, Optional, TypedDict

class ResearchState(TypedDict, total=False):
    query: str
    session_id: Optional[str]
    selected_document_ids: List[str]
    query_type: str  # "comparative", "single_paper", "synthesis", "direct"
    research_plan: List[str]
    subtasks: List[str]
    retrieved_evidence: List[Dict[str, Any]]
    evidence_extractions: List[Dict[str, Any]]
    multi_paper_analysis: str
    synthesized_answer: str
    validated_citations: List[Dict[str, Any]]
    final_response: str
    steps_taken: List[Dict[str, Any]]
    db_session: Any

