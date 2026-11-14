from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from backend.app.agents.state import ResearchState
from backend.app.agents.nodes import (
    query_understanding_node,
    conversational_handler_node,
    summarization_handler_node,
    comparative_full_handler_node,
    research_planning_node,
    subtask_generation_node,
    document_retrieval_node,
    evidence_extraction_node,
    multi_paper_analysis_node,
    answer_synthesis_node,
    citation_validation_node
)

def route_after_understanding(state: ResearchState) -> str:
    q_type = state.get("query_type", "direct")
    if q_type in ["conversational", "meta_corpus"]:
        return "conversational_handler"
    if q_type == "summarization":
        return "summarization_handler"
    if q_type == "comparative_full":
        return "comparative_full_handler"
    if q_type == "direct":
        return "document_retrieval"
    return "research_planning"

def route_after_extraction(state: ResearchState) -> str:
    q_type = state.get("query_type", "direct")
    if q_type == "comparative":
        return "multi_paper_analysis"
    return "answer_synthesis"

def build_research_graph():
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("query_understanding", query_understanding_node)
    workflow.add_node("conversational_handler", conversational_handler_node)
    workflow.add_node("summarization_handler", summarization_handler_node)
    workflow.add_node("comparative_full_handler", comparative_full_handler_node)
    workflow.add_node("research_planning", research_planning_node)
    workflow.add_node("subtask_generation", subtask_generation_node)
    workflow.add_node("document_retrieval", document_retrieval_node)
    workflow.add_node("evidence_extraction", evidence_extraction_node)
    workflow.add_node("multi_paper_analysis", multi_paper_analysis_node)
    workflow.add_node("answer_synthesis", answer_synthesis_node)
    workflow.add_node("citation_validation", citation_validation_node)

    # Set Entry Point
    workflow.set_entry_point("query_understanding")

    # Conditional routing after understanding
    workflow.add_conditional_edges(
        "query_understanding",
        route_after_understanding,
        {
            "conversational_handler": "conversational_handler",
            "summarization_handler": "summarization_handler",
            "comparative_full_handler": "comparative_full_handler",
            "document_retrieval": "document_retrieval",
            "research_planning": "research_planning"
        }
    )

    workflow.add_edge("conversational_handler", END)
    workflow.add_edge("summarization_handler", END)
    workflow.add_edge("comparative_full_handler", END)
    workflow.add_edge("research_planning", "subtask_generation")
    workflow.add_edge("subtask_generation", "document_retrieval")
    workflow.add_edge("document_retrieval", "evidence_extraction")

    # Conditional routing after extraction
    workflow.add_conditional_edges(
        "evidence_extraction",
        route_after_extraction,
        {
            "multi_paper_analysis": "multi_paper_analysis",
            "answer_synthesis": "answer_synthesis"
        }
    )

    workflow.add_edge("multi_paper_analysis", "answer_synthesis")
    workflow.add_edge("answer_synthesis", "citation_validation")
    workflow.add_edge("citation_validation", END)

    return workflow.compile()

research_graph = build_research_graph()

def run_research_workflow(
    query: str,
    db_session: Any,
    session_id: Optional[str] = None,
    selected_document_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    initial_state: ResearchState = {
        "query": query,
        "session_id": session_id,
        "selected_document_ids": selected_document_ids or [],
        "steps_taken": [],
        "db_session": db_session
    }

    result_state = research_graph.invoke(initial_state)
    return result_state

