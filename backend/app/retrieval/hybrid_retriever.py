import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.embeddings.vector_store import vector_store
from backend.app.retrieval.bm25_retriever import bm25_retriever
from backend.app.retrieval.reranker import reranker

class HybridRetriever:
    def __init__(
        self,
        semantic_weight: float = 0.65,
        bm25_weight: float = 0.35,
        rrf_k: int = 60
    ):
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.rrf_k = rrf_k

    def _expand_query(self, query: str) -> List[str]:
        """
        Academic query expansion: adds domain-specific keywords and synonyms
        to maximize candidate recall for tables, metrics, and architecture.
        """
        queries = [query]
        q_lower = query.lower()

        if any(w in q_lower for w in ["bleu", "score", "metric", "accuracy", "f1", "result", "performance"]):
            queries.append(f"{query} experimental results benchmark evaluation table")
        if any(w in q_lower for w in ["architecture", "scaled dot", "attention", "mechanism", "encoder", "decoder"]):
            queries.append(f"{query} model architecture multi-head attention formulation")
        if any(w in q_lower for w in ["dataset", "data", "corpus", "train", "training"]):
            queries.append(f"{query} pre-training corpus dataset size sentences words")
        if any(w in q_lower for w in ["compare", "versus", "vs", "difference"]):
            queries.append(f"{query} methodology architecture comparison results")

        return queries

    def retrieve(
        self,
        query: str,
        db: Session,
        filter_doc_ids: Optional[List[str]] = None,
        top_k: int = settings.TOP_K_RERANK,
        candidate_pool_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Execute Advanced Hybrid Retrieval:
        1. Multi-query expansion across semantic and lexical representations
        2. ChromaDB dense semantic vector search (SentenceTransformer embeddings)
        3. BM25+ token-level keyword search
        4. Reciprocal Rank Fusion (RRF) with semantic and BM25 weights
        5. Deep neural Cross-Encoder reranking
        """
        expanded_queries = self._expand_query(query)

        # 1. Semantic Retrieval across expanded queries
        semantic_hits_map: Dict[str, Dict[str, Any]] = {}
        for q in expanded_queries:
            hits = vector_store.search(
                query=q,
                top_k=candidate_pool_size,
                filter_doc_ids=filter_doc_ids
            )
            for h in hits:
                cid = h["id"]
                if cid not in semantic_hits_map or h.get("score", 0.0) > semantic_hits_map[cid].get("score", 0.0):
                    semantic_hits_map[cid] = h

        # 2. BM25 Retrieval across expanded queries
        bm25_hits_map: Dict[str, Dict[str, Any]] = {}
        for q in expanded_queries:
            hits = bm25_retriever.search_database(
                query=q,
                db=db,
                filter_doc_ids=filter_doc_ids,
                top_k=candidate_pool_size
            )
            for h in hits:
                cid = h["id"]
                if cid not in bm25_hits_map or h.get("score", 0.0) > bm25_hits_map[cid].get("score", 0.0):
                    bm25_hits_map[cid] = h

        # 3. Merge & Deduplicate with Reciprocal Rank Fusion
        merged_candidates: Dict[str, Dict[str, Any]] = {}

        # Add semantic hits
        sorted_semantic = sorted(semantic_hits_map.values(), key=lambda x: x.get("score", 0.0), reverse=True)
        for rank, hit in enumerate(sorted_semantic):
            cid = hit["id"]
            rrf_score = 1.0 / (self.rrf_k + rank + 1)
            merged_candidates[cid] = {
                **hit,
                "rrf_score": rrf_score,
                "semantic_score": hit.get("score", 0.0),
                "bm25_score": 0.0,
                "retrieval_source": "semantic"
            }

        # Add / update BM25 hits
        sorted_bm25 = sorted(bm25_hits_map.values(), key=lambda x: x.get("score", 0.0), reverse=True)
        for rank, hit in enumerate(sorted_bm25):
            cid = hit["id"]
            rrf_score = 1.0 / (self.rrf_k + rank + 1)
            if cid in merged_candidates:
                merged_candidates[cid]["rrf_score"] += rrf_score
                merged_candidates[cid]["bm25_score"] = hit.get("score", 0.0)
                merged_candidates[cid]["retrieval_source"] = "hybrid"
            else:
                merged_candidates[cid] = {
                    **hit,
                    "rrf_score": rrf_score,
                    "semantic_score": 0.0,
                    "bm25_score": hit.get("score", 0.0),
                    "retrieval_source": "bm25"
                }

        # Compute initial combined score
        for c in merged_candidates.values():
            c["score"] = (
                self.semantic_weight * c.get("semantic_score", 0.0) +
                self.bm25_weight * min(1.0, c.get("bm25_score", 0.0) / 10.0) +
                c.get("rrf_score", 0.0)
            )

        candidate_list = list(merged_candidates.values())
        candidate_list.sort(key=lambda x: x["score"], reverse=True)

        # Form candidate pool for reranker
        pool = candidate_list[:candidate_pool_size]

        # 4. Neural Cross-Encoder Reranking
        final_results = reranker.rerank(query=query, candidates=pool, top_k=top_k)
        return final_results

hybrid_retriever = HybridRetriever()
