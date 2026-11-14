import pytest
from backend.app.retrieval.chunker import chunker

def test_chunker_cleaning_and_structure():
    raw_text = """
    arXiv:1706.03762v5 [cs.CL] 6 Dec 2017
    1. Introduction
    This is an intro paragraph describing deep trans-
    formers in neural networks.

    3
    2. Background
    This is the background section discussing convolutional models.
    """
    cleaned = chunker.clean_text(raw_text)
    assert "arXiv" not in cleaned
    assert "transformers" in cleaned
    assert "\n    3\n" not in cleaned

    chunks = chunker.chunk_page(
        page_number=1,
        raw_text=raw_text,
        document_id="doc_123",
        paper_title="Transformer Paper"
    )
    assert len(chunks) >= 1
    for c in chunks:
        assert c["page_number"] == 1
        assert c["document_id"] == "doc_123"
        assert c["paper_title"] == "Transformer Paper"
        assert "content" in c

