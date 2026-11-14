import pytest
from backend.app.retrieval.bm25_retriever import bm25_retriever
from backend.app.retrieval.reranker import reranker
from backend.app.retrieval.hybrid_retriever import hybrid_retriever
from backend.app.embeddings.vector_store import vector_store

def test_bm25_retrieval():
    corpus = [
        {
            "id": "c1",
            "content": "The Transformer uses multi-head self-attention mechanisms without recurrence.",
            "metadata": {"paper_title": "Attention", "page_number": 2, "document_id": "d1"}
        },
        {
            "id": "c2",
            "content": "Convolutional networks like ConvS2S process tokens with linear distance growth.",
            "metadata": {"paper_title": "ConvS2S", "page_number": 1, "document_id": "d2"}
        }
    ]
    results = bm25_retriever.search_chunks(query="multi-head self-attention", chunks=corpus, top_k=2)
    assert len(results) > 0
    assert results[0]["id"] == "c1"
    assert results[0]["score"] > 0

def test_cross_encoder_reranker():
    candidates = [
        {"id": "1", "content": "The weather in Seattle is rainy.", "score": 0.5},
        {"id": "2", "content": "Transformer models achieve high BLEU scores on translation.", "score": 0.6}
    ]
    query = "translation BLEU score transformer"
    reranked = reranker.rerank(query=query, candidates=candidates, top_k=2)
    assert len(reranked) == 2
    assert reranked[0]["id"] == "2"

