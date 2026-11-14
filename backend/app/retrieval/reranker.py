import re
import math
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

class CrossEncoderReranker:
    def __init__(self, model_name: str = settings.RERANKER_MODEL_NAME):
        self.model_name = model_name
        self._ce_model = None
        self._fallback_mode = False

    def _get_model(self):
        if self._ce_model is None and not self._fallback_mode:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"Loading CrossEncoder reranker model: {self.model_name}")
                self._ce_model = CrossEncoder(self.model_name)
                logger.info("CrossEncoder reranker model loaded successfully.")
            except Exception as e:
                logger.warning(f"CrossEncoder load failed ({e}), using lexical reranker.")
                self._fallback_mode = True
        return self._ce_model

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = settings.TOP_K_RERANK
    ) -> List[Dict[str, Any]]:
        """
        Rerank retrieved candidate chunks using deep neural CrossEncoder or Lexical-Semantic Matcher.
        """
        if not candidates:
            return []

        model = self._get_model()

        if model is not None:
            try:
                pairs = [[query, c.get("content", "")] for c in candidates]
                scores = model.predict(pairs, show_progress_bar=False)

                for idx, raw_score in enumerate(scores):
                    s = float(raw_score)
                    # Sigmoid transform to normalize logit to (0, 1) confidence score
                    prob = 1.0 / (1.0 + math.exp(-s))
                    candidates[idx]["cross_encoder_logit"] = s
                    candidates[idx]["cross_encoder_score"] = round(prob, 4)
                    
                    # Fuse cross-encoder confidence with initial hybrid RRF score
                    initial_score = candidates[idx].get("score", 0.0)
                    candidates[idx]["rerank_score"] = round(0.75 * prob + 0.25 * min(1.0, initial_score), 4)
                    candidates[idx]["final_score"] = candidates[idx]["rerank_score"]
            except Exception as e:
                logger.warning(f"CrossEncoder scoring error ({e}). Falling back to lexical ranking.")
                model = None

        if model is None:
            q_terms = set(re.findall(r"\w{3,}", query.lower()))
            for c in candidates:
                c_text = c.get("content", "").lower()
                c_words = set(re.findall(r"\w{3,}", c_text))
                overlap = len(q_terms.intersection(c_words)) / max(1, len(q_terms))
                combined = c.get("score", 0.0) + (1.5 * overlap)
                c["rerank_score"] = round(combined, 4)
                c["final_score"] = round(combined, 4)

        reranked = sorted(candidates, key=lambda x: x.get("final_score", 0.0), reverse=True)
        return reranked[:top_k]

reranker = CrossEncoderReranker()
