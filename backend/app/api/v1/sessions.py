import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import ResearchSession, ChatMessage
from backend.app.schemas.chat import (
    SessionCreate,
    SessionResponse,
    MessageResponse,
    Citation,
    AgentStep
)
from backend.app.services.session_service import session_service

router = APIRouter(prefix="/sessions", tags=["Research Sessions"])

@router.post("", response_model=SessionResponse)
def create_session(request: SessionCreate, db: Session = Depends(get_db)):
    """Create a new research session."""
    session = session_service.create_session(
        title=request.title or "New Research Session",
        topic=request.topic or "General Research",
        selected_document_ids=request.selected_document_ids or [],
        db=db
    )
    return SessionResponse(
        id=session.id,
        title=session.title,
        topic=session.topic,
        selected_document_ids=json.loads(session.selected_document_ids or "[]"),
        rolling_summary=session.rolling_summary or "",
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[]
    )

@router.get("", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    """List all research sessions."""
    sessions = session_service.list_sessions(db)
    results = []
    for s in sessions:
        results.append(SessionResponse(
            id=s.id,
            title=s.title,
            topic=s.topic,
            selected_document_ids=json.loads(s.selected_document_ids or "[]"),
            rolling_summary=s.rolling_summary or "",
            created_at=s.created_at,
            updated_at=s.updated_at,
            messages=[]
        ))
    return results

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get research session by ID with complete chat history."""
    session = session_service.get_session(session_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    msgs = []
    for m in session.messages:
        citations = [Citation(**c) for c in json.loads(m.citations or "[]")]
        steps = [AgentStep(**s) for s in json.loads(m.agent_steps or "[]")]
        msgs.append(MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            citations=citations,
            agent_steps=steps,
            created_at=m.created_at
        ))

    return SessionResponse(
        id=session.id,
        title=session.title,
        topic=session.topic,
        selected_document_ids=json.loads(session.selected_document_ids or "[]"),
        rolling_summary=session.rolling_summary or "",
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=msgs
    )

@router.put("/{session_id}/documents", response_model=SessionResponse)
def update_selected_documents(
    session_id: str,
    doc_ids: List[str],
    db: Session = Depends(get_db)
):
    """Update active paper selection for session."""
    session = session_service.update_session_selection(session_id, doc_ids, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    return SessionResponse(
        id=session.id,
        title=session.title,
        topic=session.topic,
        selected_document_ids=json.loads(session.selected_document_ids or "[]"),
        rolling_summary=session.rolling_summary or "",
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[]
    )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete research session and its chat history."""
    session = session_service.get_session(session_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    db.delete(session)
    db.commit()
    return None

