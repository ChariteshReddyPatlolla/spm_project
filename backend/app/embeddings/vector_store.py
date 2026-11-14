import os
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.embeddings.embedding_service import embedding_service

class ChromaVectorStore:
    def __init__(self, persist_dir: str = settings.CHROMA_DIR, collection_name: str = "research_papers"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            import chromadb
            from chromadb.config import Settings
            logger.info(f"Initializing ChromaDB vector store at: {self.persist_dir}")
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Add structure-aware chunks to ChromaDB.
        Each chunk dict: id, document_id, paper_title, page_number, section_title, content
        """
        if not chunks:
            return

        collection = self._get_collection()

        ids = [c["id"] for c in chunks]
        texts = [c["content"] for c in chunks]
        metadatas = [
            {
                "document_id": str(c["document_id"]),
                "paper_title": str(c.get("paper_title", "Untitled")),
                "page_number": int(c.get("page_number", 1)),
                "section_title": str(c.get("section_title", "General")),
                "chunk_id": str(c["id"])
            }
            for c in chunks
        ]

        embeddings = embedding_service.embed_documents(texts)

        # Batch upsert in chunks of 100 to avoid payload size limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=texts[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

        logger.info(f"Successfully added {len(chunks)} chunks to ChromaDB collection '{self.collection_name}'")

    def search(
        self,
        query: str,
        top_k: int = settings.TOP_K_RETRIEVAL,
        filter_doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search with optional document ID filtering.
        """
        collection = self._get_collection()
        query_embedding = embedding_service.embed_query(query)

        where_clause = None
        if filter_doc_ids:
            if len(filter_doc_ids) == 1:
                where_clause = {"document_id": {"$eq": filter_doc_ids[0]}}
            elif len(filter_doc_ids) > 1:
                where_clause = {"document_id": {"$in": filter_doc_ids}}

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.error(f"ChromaDB search query failed: {e}")
            return []

        hits: List[Dict[str, Any]] = []
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                text = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i]
                # Cosine similarity roughly 1 - distance
                similarity = max(0.0, 1.0 - dist)
                hits.append({
                    "id": doc_id,
                    "content": text,
                    "metadata": meta,
                    "score": similarity,
                    "retrieval_source": "semantic"
                })

        return hits

    def delete_document_vectors(self, document_id: str):
        collection = self._get_collection()
        try:
            collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted vectors for document {document_id}")
        except Exception as e:
            logger.warning(f"ChromaDB vector deletion note: {e}")

vector_store = ChromaVectorStore()

