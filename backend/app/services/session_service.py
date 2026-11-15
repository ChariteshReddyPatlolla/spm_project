import json
import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.core.logging import logger
from backend.app.database.models import ResearchSession, ChatMessage, Document
from backend.app.schemas.chat import (
    SessionResponse,
    MessageResponse,
    Citation,
    AgentStep
)
from backend.app.services.llm_service import llm_service

class SessionService:
    @staticmethod
    def create_session(
        title: str,
        topic: str,
        selected_document_ids: List[str],
        db: Session
    ) -> ResearchSession:
        session = ResearchSession(
            id=str(uuid.uuid4()),
            title=title or "New Research Session",
            topic=topic or "General Research",
            selected_document_ids=json.dumps(selected_document_ids or [])
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(session_id: str, db: Session) -> Optional[ResearchSession]:
        return db.query(ResearchSession).filter(ResearchSession.id == session_id).first()

    @staticmethod
    def list_sessions(db: Session) -> List[ResearchSession]:
        return db.query(ResearchSession).order_by(ResearchSession.updated_at.desc()).all()

    @staticmethod
    def update_session_selection(
        session_id: str,
        selected_document_ids: List[str],
        db: Session
    ) -> Optional[ResearchSession]:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if session:
            session.selected_document_ids = json.dumps(selected_document_ids)
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session

    @classmethod
    def resolve_follow_up_query(
        cls,
        session_id: str,
        raw_query: str,
        db: Session
    ) -> Tuple[str, List[str]]:
        """
        Resolve contextual references in user query (e.g. 'Compare the first two papers',
        'Explain that methodology in detail', 'What limitations did the second paper have?').
        Returns: (resolved_query, active_selected_document_ids)
        """
        session = cls.get_session(session_id, db)
        if not session:
            return raw_query, []

        selected_ids: List[str] = json.loads(session.selected_document_ids or "[]")
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(6).all()
        recent_messages.reverse()

        # If query has ordinal or deictic references, resolve them using paper titles
        if selected_ids:
            doc_records = db.query(Document).filter(Document.id.in_(selected_ids)).all()
        else:
            doc_records = db.query(Document).all()
        paper_index_map = {idx + 1: d for idx, d in enumerate(doc_records)}

        resolved_query = raw_query

        # Resolve "the first two papers"
        if re.search(r"\b(first two papers|first 2 papers)\b", raw_query, re.IGNORECASE) and len(doc_records) >= 2:
            p1 = doc_records[0].title
            p2 = doc_records[1].title
            resolved_query = re.sub(
                r"\b(first two papers|first 2 papers)\b",
                f"'{p1}' and '{p2}'",
                resolved_query,
                flags=re.IGNORECASE
            )

        # Resolve "the first paper"
        if re.search(r"\b(first paper|1st paper)\b", raw_query, re.IGNORECASE) and len(doc_records) >= 1:
            p1 = doc_records[0].title
            resolved_query = re.sub(
                r"\b(first paper|1st paper)\b",
                f"'{p1}'",
                resolved_query,
                flags=re.IGNORECASE
            )
            selected_ids = [doc_records[0].id]

        # Resolve "the second paper"
        if re.search(r"\b(second paper|2nd paper)\b", raw_query, re.IGNORECASE) and len(doc_records) >= 2:
            p2 = doc_records[1].title
            resolved_query = re.sub(
                r"\b(second paper|2nd paper)\b",
                f"'{p2}'",
                resolved_query,
                flags=re.IGNORECASE
            )
            selected_ids = [doc_records[1].id]

        # Resolve "that methodology" or "that architecture" from last assistant response
        if any(w in raw_query.lower() for w in ["that methodology", "that approach", "that architecture", "those results"]):
            if recent_messages:
                last_asst = [m for m in recent_messages if m.role == "assistant"]
                if last_asst:
                    last_content = last_asst[-1].content
                    # Extract leading context
                    resolved_query = f"{resolved_query} (Context from prior discussion: {last_content[:150]})"

        # Update rolling session summary if conversation is growing
        if len(recent_messages) >= 4 and not session.rolling_summary:
            cls._update_rolling_summary(session, recent_messages, db)

        return resolved_query, selected_ids

    @staticmethod
    def _update_rolling_summary(session: ResearchSession, messages: List[ChatMessage], db: Session):
        summary_prompt = (
            "Summarize the key research findings discussed in this conversation in 2-3 sentences:\n"
            + "\n".join([f"{m.role}: {m.content[:200]}" for m in messages])
        )
        try:
            summary = llm_service.generate_sync(summary_prompt)
            session.rolling_summary = summary
            db.commit()
        except Exception as e:
            logger.warning(f"Could not update rolling summary: {e}")

    @staticmethod
    def add_message(
        session_id: str,
        role: str,
        content: str,
        citations: List[Dict[str, Any]],
        agent_steps: List[Dict[str, Any]],
        db: Session
    ) -> ChatMessage:
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            citations=json.dumps(citations),
            agent_steps=json.dumps(agent_steps)
        )
        db.add(msg)

        # Update session timestamp
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(msg)
        return msg

session_service = SessionService()
