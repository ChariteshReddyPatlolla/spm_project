import pytest
from backend.app.services.comparative_service import comparative_service
from backend.app.ingestion.pdf_processor import pdf_processor
from backend.app.retrieval.chunker import chunker
from backend.app.database.models import DocumentChunk, DocumentPage

def test_comparative_analysis(db_session):
    # Ingest two papers
    with open("sample_papers/attention_paper.pdf", "rb") as f:
        doc1 = pdf_processor.process_pdf(f.read(), "attention_paper.pdf", db_session)
    with open("sample_papers/bert_paper.pdf", "rb") as f:
        doc2 = pdf_processor.process_pdf(f.read(), "bert_paper.pdf", db_session)

    # Chunk both if not already chunked
    for doc in [doc1, doc2]:
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

    resp = comparative_service.analyze_papers(
        document_ids=[doc1.id, doc2.id],
        db=db_session
    )

    assert resp.id is not None
    assert len(resp.comparison_table) >= 8
    assert len(resp.advantages_disadvantages) == 2
    assert len(resp.detailed_analysis) > 50
    assert len(resp.research_gaps) > 20
