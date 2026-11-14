import pytest
from backend.app.agents.research_graph import run_research_workflow
from backend.app.ingestion.pdf_processor import pdf_processor
from backend.app.retrieval.chunker import chunker
from backend.app.database.models import DocumentChunk, DocumentPage

def test_agentic_workflow_execution(db_session):
    with open("sample_papers/attention_paper.pdf", "rb") as f:
        doc = pdf_processor.process_pdf(f.read(), "attention_paper.pdf", db_session)

    existing = db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
    if existing == 0:
        pages = db_session.query(DocumentPage).filter(DocumentPage.document_id == doc.id).all()
        for p in pages:
            chunks = chunker.chunk_page(p.page_number, p.text_content, doc.id, doc.title)
            for c in chunks:
                db_session.add(DocumentChunk(
                    id=c["id"],
                    document_id=doc.id,
                    chunk_index=0,
                    page_number=c["page_number"],
                    section_title=c["section_title"],
                    content=c["content"],
                    token_count=c["token_count"],
                    char_count=c["char_count"]
                ))
        db_session.commit()

    result = run_research_workflow(
        query="What is Scaled Dot-Product Attention?",
        db_session=db_session,
        selected_document_ids=[doc.id]
    )

    assert "final_response" in result
    assert len(result["steps_taken"]) >= 4
    step_names = [s["step_name"] for s in result["steps_taken"]]
    assert "Query Understanding" in step_names
    assert "Document Retrieval" in step_names
    assert "Answer Synthesis" in step_names
    assert "Citation Validation" in step_names
