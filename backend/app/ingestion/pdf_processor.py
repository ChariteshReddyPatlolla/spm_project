import os
import hashlib
import json
import uuid
import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.models import Document, DocumentPage
from backend.app.ingestion.metadata_extractor import MetadataExtractor
from backend.app.ingestion.ocr_processor import ocr_processor

class PDFProcessor:
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        return hasher.hexdigest()

    @staticmethod
    def extract_clean_text_from_page(page) -> Tuple[str, bool, bool, bool]:
        """
        Extract clean, layout-aware text from a PyMuPDF page.
        Returns: (text, has_images, has_tables, is_ocr)
        """
        has_images = len(page.get_images()) > 0
        has_tables = False
        is_ocr = False

        # Check for tables
        try:
            tables = page.find_tables()
            if tables and len(tables.tables) > 0:
                has_tables = True
        except Exception:
            pass

        # Multi-column sorting: get_text("blocks") returns blocks sorted in reading order
        # Each block: (x0, y0, x1, y1, text, block_no, block_type)
        # block_type == 0 is text
        blocks = page.get_text("blocks", sort=True)
        text_blocks = []
        for b in blocks:
            if len(b) >= 5 and b[6] == 0:  # text block
                cleaned = b[4].strip()
                if cleaned:
                    text_blocks.append(cleaned)

        extracted_text = "\n\n".join(text_blocks).strip()

        # Check if text is sparse and has images -> Scanned PDF OCR fallback
        if len(extracted_text) < 40 and has_images and ocr_processor.is_available():
            try:
                pix = page.get_pixmap(dpi=150)
                ocr_text = ocr_processor.ocr_pixmap(pix)
                if len(ocr_text) > len(extracted_text):
                    extracted_text = ocr_text
                    is_ocr = True
            except Exception as e:
                logger.warning(f"OCR fallback failed on page {page.number + 1}: {e}")

        # Table formatting integration
        if has_tables:
            try:
                table_mds = []
                for t in tables.tables:
                    df_data = t.extract()
                    if df_data and len(df_data) > 1:
                        # Format as markdown table
                        header = [str(c or "").strip() for c in df_data[0]]
                        header_line = "| " + " | ".join(header) + " |"
                        sep_line = "| " + " | ".join(["---"] * len(header)) + " |"
                        row_lines = []
                        for r in df_data[1:]:
                            row_lines.append("| " + " | ".join([str(c or "").strip() for c in r]) + " |")
                        table_md = "\n".join([header_line, sep_line] + row_lines)
                        table_mds.append(table_md)
                if table_mds:
                    extracted_text += "\n\n[Extracted Tables]:\n" + "\n\n".join(table_mds)
            except Exception as e:
                logger.warning(f"Failed to format table markdown: {e}")

        return extracted_text, has_images, has_tables, is_ocr

    @classmethod
    def process_pdf(cls, file_bytes: bytes, filename: str, db: Session) -> Document:
        """
        Process an uploaded PDF:
        - Check for duplicate hash
        - Create Document record
        - Extract pages with PyMuPDF
        - Extract metadata (title, authors, abstract, year)
        - Commit Document and DocumentPage rows
        """
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz

        file_hash = cls.calculate_file_hash(file_bytes)

        # Duplicate check
        existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
        if existing_doc:
            logger.info(f"Duplicate document detected: {filename} matches {existing_doc.id}")
            return existing_doc

        doc_id = str(uuid.uuid4())
        save_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{filename}")
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Create initial Document record
        document = Document(
            id=doc_id,
            filename=filename,
            file_path=save_path,
            file_hash=file_hash,
            status="processing"
        )
        db.add(document)
        db.commit()

        try:
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(pdf_doc)
            document.page_count = total_pages

            # Extract first page blocks for metadata
            page_1 = pdf_doc[0] if total_pages > 0 else None
            page_1_dict = page_1.get_text("dict") if page_1 else {"blocks": []}
            page_1_raw_text = page_1.get_text("text") if page_1 else ""

            # Extract metadata
            meta = MetadataExtractor.extract_from_blocks(
                blocks=page_1_dict.get("blocks", []),
                page_1_text=page_1_raw_text,
                doc_metadata=pdf_doc.metadata
            )

            document.title = meta["title"]
            document.authors = json.dumps(meta["authors"])
            document.abstract = meta["abstract"]
            document.year = meta["year"]

            # Process all pages
            for page_idx in range(total_pages):
                page = pdf_doc[page_idx]
                page_num = page_idx + 1  # 1-indexed

                page_text, has_images, has_tables, is_ocr = cls.extract_clean_text_from_page(page)

                page_record = DocumentPage(
                    document_id=doc_id,
                    page_number=page_num,
                    text_content=page_text,
                    has_images=has_images,
                    has_tables=has_tables,
                    is_ocr=is_ocr
                )
                db.add(page_record)

            document.status = "ready"
            db.commit()
            db.refresh(document)
            pdf_doc.close()
            return document

        except Exception as e:
            logger.error(f"Failed to process PDF {filename}: {e}", exc_info=True)
            document.status = "failed"
            document.error_message = str(e)
            db.commit()
            raise e

    @classmethod
    def delete_document(cls, document_id: str, db: Session, chroma_collection=None) -> bool:
        """
        Delete document, its pages, its chunks, its physical file, and ChromaDB vectors.
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        # Delete physical file
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                logger.warning(f"Could not delete physical file {document.file_path}: {e}")

        # Delete from ChromaDB
        if chroma_collection is not None:
            try:
                chroma_collection.delete(where={"document_id": document_id})
                logger.info(f"Deleted vectors for document {document_id} from ChromaDB")
            except Exception as e:
                logger.warning(f"Error deleting vectors from ChromaDB: {e}")

        # Delete from SQLite (cascades to pages, chunks, summary)
        db.delete(document)
        db.commit()
        return True

pdf_processor = PDFProcessor()

