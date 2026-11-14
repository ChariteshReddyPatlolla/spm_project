import pytest
from backend.app.services.summarization_service import summarization_service
from backend.app.ingestion.pdf_processor import pdf_processor

def test_paper_summarization(db_session):
    with open("sample_papers/bert_paper.pdf", "rb") as f:
        doc = pdf_processor.process_pdf(f.read(), "bert_paper.pdf", db_session)

    summary = summarization_service.get_or_generate_summary(
        document_id=doc.id,
        db=db_session
    )

    assert summary.document_id == doc.id
    assert len(summary.research_objective) > 10
    assert len(summary.methodology) > 10
    assert len(summary.proposed_architecture) > 10
    assert len(summary.algorithms_and_models) > 10
    assert len(summary.datasets) > 10
    assert len(summary.evaluation_metrics) > 10
    assert len(summary.experimental_results) > 10
    assert len(summary.main_contributions) > 10
    assert len(summary.limitations) > 10
    assert len(summary.future_research_directions) > 10

    # Test cache: calling again returns the cached record
    cached = summarization_service.get_or_generate_summary(
        document_id=doc.id,
        db=db_session
    )
    assert cached.id == summary.id

