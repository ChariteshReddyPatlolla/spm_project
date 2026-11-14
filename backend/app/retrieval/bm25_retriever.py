import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Plus
from sqlalchemy.orm import Session
from backend.app.database.models import DocumentChunk, Document
from backend.app.core.logging import logger

class BM25Retriever:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple, fast tokenization for BM25."""
        return re.findall(r"\w+", text.lower())

    @classmethod
    def search_chunks(
        cls,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Execute BM25 keyword search over a list of chunk dicts using BM25+ (handles small & large corpora).
        Each chunk dict: id, content, metadata
        """
        if not chunks:
            return []

        tokenized_corpus = [cls.tokenize(c["content"]) for c in chunks]
        bm25 = BM25Plus(tokenized_corpus)
        tokenized_query = cls.tokenize(query)

        if not tokenized_query:
            return []

        scores = bm25.get_scores(tokenized_query)

        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0

        scored_chunks = []
        for idx, score in enumerate(scores):
            if score > 0:
                chunk = chunks[idx]
                scored_chunks.append({
                    "id": chunk["id"],
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "score": float(score / max_score),
                    "raw_score": float(score),
                    "retrieval_source": "bm25"
                })

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    @classmethod
    def search_database(
        cls,
        query: str,
        db: Session,
        filter_doc_ids: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Load chunks from SQLite for the given documents and run BM25 search.
        """
        query_set = db.query(DocumentChunk, Document.title).join(
            Document, DocumentChunk.document_id == Document.id
        )

        if filter_doc_ids:
            query_set = query_set.filter(DocumentChunk.document_id.in_(filter_doc_ids))

        db_chunks = query_set.all()
        if not db_chunks:
            return []

        chunk_dicts = [
            {
                "id": c.DocumentChunk.id,
                "content": c.DocumentChunk.content,
                "metadata": {
                    "document_id": c.DocumentChunk.document_id,
                    "paper_title": c.title,
                    "page_number": c.DocumentChunk.page_number,
                    "section_title": c.DocumentChunk.section_title,
                    "chunk_id": c.DocumentChunk.id
                }
            }
            for c in db_chunks
        ]

        return cls.search_chunks(query, chunk_dicts, top_k=top_k)

bm25_retriever = BM25Retriever()
