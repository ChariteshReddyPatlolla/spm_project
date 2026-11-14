import os
import pytest
from backend.app.ingestion.pdf_processor import pdf_processor
from backend.app.database.models import Document, DocumentPage

def test_pdf_ingestion_and_metadata(db_session):
    pdf_path = "sample_papers/attention_paper.pdf"
    assert os.path.exists(pdf_path)

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    doc = pdf_processor.process_pdf(file_bytes=file_bytes, filename="attention_paper.pdf", db=db_session)

    assert doc.id is not None
    assert doc.status == "ready"
    assert doc.page_count == 4
    assert "Attention Is All You Need" in doc.title
    assert "Vaswani" in doc.authors or "Ashish" in doc.authors or len(doc.authors) > 0
    assert len(doc.abstract) > 30

    # Verify pages retained exact 1-indexed numbers and doc_id
    pages = db_session.query(DocumentPage).filter(DocumentPage.document_id == doc.id).all()
    assert len(pages) == 4
    page_numbers = [p.page_number for p in pages]
    assert page_numbers == [1, 2, 3, 4]

    # Verify duplicate detection
    dup_doc = pdf_processor.process_pdf(file_bytes=file_bytes, filename="duplicate.pdf", db=db_session)
    assert dup_doc.id == doc.id

