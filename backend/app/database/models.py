import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Float
)
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(512), default="Untitled Document")
    authors = Column(Text, default="[]")  # JSON string
    abstract = Column(Text, default="")
    year = Column(Integer, nullable=True)
    page_count = Column(Integer, default=0)
    status = Column(String(32), default="pending")  # pending, processing, ready, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    summary = relationship("PaperSummary", back_populates="document", uselist=False, cascade="all, delete-orphan")

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)  # 1-indexed
    text_content = Column(Text, default="")
    has_images = Column(Boolean, default=False)
    has_tables = Column(Boolean, default=False)
    is_ocr = Column(Boolean, default=False)

    document = relationship("Document", back_populates="pages")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True)  # e.g., {doc_id}_c_{index}
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    section_title = Column(String(255), default="General")
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)

    document = relationship("Document", back_populates="chunks")

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), default="New Research Session")
    topic = Column(String(255), default="General Research")
    selected_document_ids = Column(Text, default="[]")  # JSON list of doc IDs
    rolling_summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    citations = Column(Text, default="[]")  # JSON list of citation objects
    agent_steps = Column(Text, default="[]")  # JSON list of execution steps
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ResearchSession", back_populates="messages")

class PaperSummary(Base):
    __tablename__ = "paper_summaries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    title = Column(String(512), default="")
    authors = Column(Text, default="")
    research_objective = Column(Text, default="")
    problem_statement = Column(Text, default="")
    methodology = Column(Text, default="")
    proposed_architecture = Column(Text, default="")
    algorithms_and_models = Column(Text, default="")
    datasets = Column(Text, default="")
    evaluation_metrics = Column(Text, default="")
    experimental_results = Column(Text, default="")
    main_contributions = Column(Text, default="")
    limitations = Column(Text, default="")
    future_research_directions = Column(Text, default="")
    citations = Column(Text, default="[]")  # JSON list of page citations
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="summary")

class ComparisonAnalysis(Base):
    __tablename__ = "comparison_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), default="Comparative Analysis")
    document_ids = Column(Text, default="[]")  # JSON list
    comparison_table = Column(Text, default="[]")  # JSON structure
    detailed_analysis = Column(Text, default="")
    advantages_disadvantages = Column(Text, default="{}")  # JSON structure
    research_gaps = Column(Text, default="")
    citations = Column(Text, default="[]")  # JSON structure
    created_at = Column(DateTime, default=datetime.utcnow)

