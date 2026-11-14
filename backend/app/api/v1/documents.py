import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Document, DocumentChunk, DocumentPage
from backend.app.schemas.document import DocumentResponse, DocumentDetail, PageInfo
from backend.app.ingestion.pdf_processor import pdf_processor
from backend.app.retrieval.chunker import chunker
from backend.app.embeddings.vector_store import vector_store
from backend.app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest multiple research papers simultaneously.
    Extracts text, metadata, runs OCR if scanned, chunks content,
    and indexes embeddings in ChromaDB.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    processed_docs: List[DocumentResponse] = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        try:
            file_bytes = await file.read()
            # Ingest PDF
            doc = pdf_processor.process_pdf(file_bytes=file_bytes, filename=file.filename, db=db)

            # Check if already chunked (e.g. duplicate upload)
            existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            if existing_chunks == 0 and doc.status == "ready":
                # Chunk and index each page
                pages = db.query(DocumentPage).filter(DocumentPage.document_id == doc.id).order_by(DocumentPage.page_number).all()
                all_chunks = []
                for p in pages:
                    p_chunks = chunker.chunk_page(
                        page_number=p.page_number,
                        raw_text=p.text_content,
                        document_id=doc.id,
                        paper_title=doc.title
                    )
                    all_chunks.extend(p_chunks)

                # Save chunks to SQLite
                for c in all_chunks:
                    db_chunk = DocumentChunk(
                        id=c["id"],
                        document_id=doc.id,
                        chunk_index=len(all_chunks),
                        page_number=c["page_number"],
                        section_title=c["section_title"],
                        content=c["content"],
                        token_count=c["token_count"],
                        char_count=c["char_count"]
                    )
                    db.add(db_chunk)
                db.commit()

                # Add to ChromaDB vector store
                if all_chunks:
                    vector_store.add_chunks(all_chunks)

            authors_list = json.loads(doc.authors) if doc.authors else []
            processed_docs.append(DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_path=doc.file_path,
                file_hash=doc.file_hash,
                title=doc.title,
                authors=authors_list,
                abstract=doc.abstract or "",
                year=doc.year,
                page_count=doc.page_count,
                status=doc.status,
                error_message=doc.error_message,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))
        except Exception as e:
            logger.error(f"Error processing upload for {file.filename}: {e}", exc_info=True)
            continue

    return processed_docs

@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded research papers."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        authors_list = json.loads(d.authors) if d.authors else []
        results.append(DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_path=d.file_path,
            file_hash=d.file_hash,
            title=d.title,
            authors=authors_list,
            abstract=d.abstract or "",
            year=d.year,
            page_count=d.page_count,
            status=d.status,
            error_message=d.error_message,
            created_at=d.created_at,
            updated_at=d.updated_at
        ))
    return results

@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document details with page summaries."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    pages = db.query(DocumentPage).filter(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number).all()
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()

    page_infos = [
        PageInfo(
            page_number=p.page_number,
            text_preview=p.text_content[:200] if p.text_content else "",
            has_images=p.has_images,
            has_tables=p.has_tables,
            is_ocr=p.is_ocr
        )
        for p in pages
    ]

    authors_list = json.loads(doc.authors) if doc.authors else []
    return DocumentDetail(
        id=doc.id,
        filename=doc.filename,
        file_path=doc.file_path,
        file_hash=doc.file_hash,
        title=doc.title,
        authors=authors_list,
        abstract=doc.abstract or "",
        year=doc.year,
        page_count=doc.page_count,
        status=doc.status,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        pages=page_infos,
        total_chunks=chunk_count
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete paper, its pages, chunks, physical file, and ChromaDB vectors.
    """
    success = pdf_processor.delete_document(
        document_id=document_id,
        db=db,
        chroma_collection=vector_store._get_collection()
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return None

