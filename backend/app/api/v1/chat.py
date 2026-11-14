import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Document, ResearchSession
from backend.app.schemas.chat import (
    ChatRequest,
    MessageResponse,
    Citation,
    AgentStep
)
from backend.app.services.session_service import session_service
from backend.app.retrieval.hybrid_retriever import hybrid_retriever
from backend.app.services.llm_service import llm_service
from backend.app.services.citation_validator import citation_validator
from backend.app.agents.research_graph import run_research_workflow
from backend.app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Research Chat"])

@router.post("", response_model=MessageResponse)
def execute_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Handle research chat queries with conversational memory,
    LangGraph agentic execution, and strict citation validation.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Manage or create research session
    session_id = request.session_id
    if not session_id:
        session = session_service.create_session(
            title=f"Research: {query[:30]}...",
            topic="Document Q&A",
            selected_document_ids=request.selected_document_ids or [],
            db=db
        )
        session_id = session.id
    else:
        session = session_service.get_session(session_id, db)
        if not session:
            session = session_service.create_session(
                title=f"Research: {query[:30]}...",
                topic="Document Q&A",
                selected_document_ids=request.selected_document_ids or [],
                db=db
            )
            session_id = session.id
        elif request.selected_document_ids:
            session_service.update_session_selection(session_id, request.selected_document_ids, db)

    # 1. Resolve follow-up conversational references
    resolved_query, active_doc_ids = session_service.resolve_follow_up_query(
        session_id=session_id,
        raw_query=query,
        db=db
    )
    # Prefer explicitly passed document IDs if present
    target_doc_ids = request.selected_document_ids if request.selected_document_ids else active_doc_ids

    # 2. Record User Message
    session_service.add_message(
        session_id=session_id,
        role="user",
        content=query,
        citations=[],
        agent_steps=[],
        db=db
    )

    # 3. Agentic Workflow vs Direct RAG
    if request.use_agentic_workflow:
        result_state = run_research_workflow(
            query=resolved_query,
            session_id=session_id,
            selected_document_ids=target_doc_ids,
            db_session=db
        )
        final_answer = result_state.get("final_response", "")
        validated_citations_dict = result_state.get("validated_citations", [])
        agent_steps_dict = result_state.get("steps_taken", [])
    else:
        # Direct Hybrid RAG
        evidence = hybrid_retriever.retrieve(
            query=resolved_query,
            db=db,
            filter_doc_ids=target_doc_ids if target_doc_ids else None,
            top_k=5
        )
        prompt = (
            f"User Query: {resolved_query}\n\nContext Chunks:\n"
            + "\n".join([f"[Document: {c['metadata']['paper_title']}, Page: {c['metadata']['page_number']}]\n{c['content']}" for c in evidence])
            + "\n\nAnswer with exact citations [Paper Title, Page X]."
        )
        raw_ans = llm_service.generate_sync(prompt)
        final_answer, citations_objs = citation_validator.validate_and_enrich_citations(
            text=raw_ans,
            retrieved_chunks=evidence
        )
        validated_citations_dict = [c.dict() for c in citations_objs]
        agent_steps_dict = [
            {"step_name": "Direct Retrieval", "description": f"Retrieved {len(evidence)} chunks via hybrid search.", "status": "completed"}
        ]

    # 4. Record Assistant Message
    assistant_msg = session_service.add_message(
        session_id=session_id,
        role="assistant",
        content=final_answer,
        citations=validated_citations_dict,
        agent_steps=agent_steps_dict,
        db=db
    )

    citations_resp = [Citation(**c) for c in validated_citations_dict]
    steps_resp = [AgentStep(**s) for s in agent_steps_dict]

    return MessageResponse(
        id=assistant_msg.id,
        session_id=session_id,
        role="assistant",
        content=final_answer,
        citations=citations_resp,
        agent_steps=steps_resp,
        created_at=assistant_msg.created_at
    )

