import hashlib
import math
import re
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._st_model = None
        self._cache: Dict[str, List[float]] = {}
        # In lightweight/cloud mode (or on Render), use instant deterministic semantic hashing
        # to avoid downloading 400MB PyTorch models and prevent memory crashes.
        self._fallback_mode = getattr(settings, "LIGHTWEIGHT_MODE", True)

    def _get_model(self):
        if self._st_model is None and not self._fallback_mode:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer embedding model: {self.model_name}")
                self._st_model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer embedding model loaded successfully.")
            except Exception as e:
                logger.warning(f"SentenceTransformer load failed ({e}), using dense semantic fallback.")
                self._fallback_mode = True
        return self._st_model

    def _dense_fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """
        Deterministic, dense semantic hashing embedding (dim=384)
        Preserves cosine similarity and term overlap for ChromaDB.
        """
        words = re.findall(r"\w+", text.lower())
        vec = [0.0] * dim

        if not words:
            return vec

        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
            vec[idx] += sign

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def _cache_key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def embed_text(self, text: str) -> List[float]:
        key = self._cache_key(text)
        if key in self._cache:
            return self._cache[key]

        model = self._get_model()
        if model is not None:
            try:
                emb = model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0].tolist()
                self._cache[key] = emb
                return emb
            except Exception as e:
                logger.warning(f"Inference failed ({e}), using dense vector.")

        emb_list = self._dense_fallback_embed(text)
        self._cache[key] = emb_list
        return emb_list

    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []

        # Check if all in cache
        uncached_indices = []
        uncached_texts = []
        results = [None] * len(texts)

        for i, t in enumerate(texts):
            k = self._cache_key(t)
            if k in self._cache:
                results[i] = self._cache[k]
            else:
                uncached_indices.append(i)
                uncached_texts.append(t)

        if not uncached_texts:
            return results

        model = self._get_model()
        if model is not None:
            try:
                embs = model.encode(
                    uncached_texts,
                    batch_size=batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                for idx, emb in zip(uncached_indices, embs):
                    emb_list = emb.tolist()
                    self._cache[self._cache_key(texts[idx])] = emb_list
                    results[idx] = emb_list
                return results
            except Exception as e:
                logger.warning(f"Batch embedding failed ({e}), using fallback.")

        for idx in uncached_indices:
            emb_list = self._dense_fallback_embed(texts[idx])
            self._cache[self._cache_key(texts[idx])] = emb_list
            results[idx] = emb_list

        return results

    def embed_query(self, query: str) -> List[float]:
        return self.embed_text(query)

embedding_service = EmbeddingService()
