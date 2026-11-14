import re
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.config import settings

class StructureAwareChunker:
    def __init__(self, chunk_size: int = settings.DEFAULT_CHUNK_SIZE, chunk_overlap: int = settings.DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing repeated headers/footers, normalizing whitespace,
        while preserving paragraphs, headings, equations, and tables.
        """
        if not text:
            return ""

        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove common academic running headers/footers (e.g., "arXiv:1706.03762v5 [cs.CL] 6 Dec 2017")
        text = re.sub(r"(?i)\barxiv:\d{4}\.\d{4,5}(v\d+)?\s*(\[[a-z\.\-]+\])?\s*.*?\n", "\n", text)
        
        # Remove standalone page number lines (e.g., "\n 12 \n")
        text = re.sub(r"\n\s*\d+\s*\n", "\n\n", text)

        # Remove repeated hyphenation at line breaks (e.g., "trans-\n   former" -> "transformer")
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

        # Normalize multiple spaces (preserving intentional double newlines)
        lines = [re.sub(r"[ \t]+", " ", line) for line in text.split("\n")]
        text = "\n".join(lines)

        # Condense 3+ newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def detect_sections(text: str) -> List[Tuple[str, str]]:
        """
        Identify section headings and split text into (section_heading, section_body) pairs.
        """
        # Common section heading patterns:
        # e.g., "1 Introduction", "2.1 Multi-Head Attention", "3 Background", "ABSTRACT", "References"
        section_pattern = re.compile(
            r"(?m)^(?:\d{1,2}(?:\.\d{1,2})*\s+[A-Z][A-Za-z0-9\s,\-\(\)]{2,50}|[A-Z\s]{4,30})$"
        )

        matches = list(section_pattern.finditer(text))
        if not matches:
            return [("General", text)]

        sections = []
        last_pos = 0
        current_title = "Introduction"

        for m in matches:
            start, end = m.span()
            # Content before this heading
            content_before = text[last_pos:start].strip()
            if content_before:
                sections.append((current_title, content_before))
            current_title = m.group(0).strip()
            last_pos = end

        remaining = text[last_pos:].strip()
        if remaining:
            sections.append((current_title, remaining))

        return sections if sections else [("General", text)]

    def chunk_page(self, page_number: int, raw_text: str, document_id: str, paper_title: str) -> List[Dict[str, Any]]:
        """
        Split a single page's text into structure-aware chunks with metadata.
        """
        cleaned_text = self.clean_text(raw_text)
        if not cleaned_text:
            return []

        sections = self.detect_sections(cleaned_text)
        chunks: List[Dict[str, Any]] = []

        chunk_idx = 0
        for section_title, section_text in sections:
            # Split section text by paragraphs
            paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]
            current_chunk = ""

            for p in paragraphs:
                if not current_chunk:
                    current_chunk = p
                elif len(current_chunk) + len(p) + 2 <= self.chunk_size:
                    current_chunk += "\n\n" + p
                else:
                    # Current chunk is full, record it
                    chunk_id = f"{document_id}_p{page_number}_c{chunk_idx}"
                    full_content = f"[{section_title}]\n{current_chunk}" if section_title != "General" else current_chunk
                    chunks.append({
                        "id": chunk_id,
                        "document_id": document_id,
                        "paper_title": paper_title,
                        "page_number": page_number,
                        "section_title": section_title,
                        "content": full_content,
                        "char_count": len(full_content),
                        "token_count": len(full_content.split())
                    })
                    chunk_idx += 1

                    # Apply overlap: take last overlap chars of current chunk
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text + "\n\n" + p
                    else:
                        current_chunk = p

            # Append any trailing chunk
            if current_chunk.strip():
                chunk_id = f"{document_id}_p{page_number}_c{chunk_idx}"
                full_content = f"[{section_title}]\n{current_chunk}" if section_title != "General" else current_chunk
                chunks.append({
                    "id": chunk_id,
                    "document_id": document_id,
                    "paper_title": paper_title,
                    "page_number": page_number,
                    "section_title": section_title,
                    "content": full_content,
                    "char_count": len(full_content),
                    "token_count": len(full_content.split())
                })
                chunk_idx += 1

        return chunks

chunker = StructureAwareChunker()
