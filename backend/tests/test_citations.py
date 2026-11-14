import pytest
from backend.app.services.citation_validator import citation_validator

def test_citation_extraction_and_validation():
    generated_text = (
        "The model achieves 28.4 BLEU on WMT 2014 [Attention Paper, Page 4] "
        "and uses multi-head attention [Attention Paper, Page 2]. "
        "It also achieved 99.9 BLEU on made up task [Fake Paper, Page 99]."
    )

    retrieved_chunks = [
        {
            "id": "c1",
            "content": "On the WMT 2014 English-to-German translation task, the model establishes a new state-of-the-art BLEU score of 28.4.",
            "final_score": 0.95,
            "metadata": {
                "document_id": "doc_att",
                "paper_title": "Attention Paper",
                "page_number": 4
            }
        },
        {
            "id": "c2",
            "content": "We call our particular attention Scaled Dot-Product Attention and Multi-Head Attention.",
            "final_score": 0.88,
            "metadata": {
                "document_id": "doc_att",
                "paper_title": "Attention Paper",
                "page_number": 2
            }
        }
    ]

    validated_text, citations = citation_validator.validate_and_enrich_citations(
        text=generated_text,
        retrieved_chunks=retrieved_chunks
    )

    # Fake paper citation was eliminated
    assert "[Fake Paper, Page 99]" not in validated_text
    assert len(citations) >= 2

    # Check citation structure
    cit_titles = [c.paper_title for c in citations]
    cit_pages = [c.page_number for c in citations]
    assert "Attention Paper" in cit_titles
    assert 4 in cit_pages
    assert 2 in cit_pages

    for c in citations:
        assert c.is_validated is True
        assert len(c.snippet) > 10
        assert c.document_id == "doc_att"

