import re
import json
from typing import Dict, List, Optional, Any

class MetadataExtractor:
    @staticmethod
    def extract_from_blocks(blocks: List[Dict[str, Any]], page_1_text: str, doc_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract title, authors, abstract, and publication year from page 1 blocks and text.
        """
        title = ""
        authors: List[str] = []
        abstract = ""
        year: Optional[int] = None

        # 1. Fallback / check document metadata first
        if doc_metadata:
            meta_title = doc_metadata.get("title", "").strip()
            ignored_titles = ["(anonymous)", "untitled", "none", "document", "default"]
            if meta_title and len(meta_title) > 5 and not meta_title.lower().endswith(".pdf") and meta_title.lower() not in ignored_titles:
                title = meta_title
            meta_author = doc_metadata.get("author", "").strip()
            if meta_author and meta_author.lower() not in ignored_titles:
                authors = [a.strip() for a in re.split(r"[,;]\s*", meta_author) if a.strip()]

        # 2. Extract Title from largest font blocks in top half of page 1
        if not title and blocks:
            # Sort text spans by font size descending
            spans_with_size = []
            for b in blocks:
                # b can be a block dict with "lines"
                if "lines" in b:
                    for line in b["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            size = span.get("size", 0)
                            bbox = span.get("bbox", (0, 0, 0, 0))
                            # Only consider top 45% of page
                            if bbox[1] < 400 and len(text) > 3:
                                spans_with_size.append((size, text, bbox))

            if spans_with_size:
                # Find maximum font size
                max_size = max(s[0] for s in spans_with_size)
                # Collect text belonging to title (font size within 1pt of max_size)
                title_spans = [s for s in spans_with_size if s[0] >= (max_size - 1.5)]
                # Sort by y, then x
                title_spans.sort(key=lambda s: (round(s[2][1], -1), s[2][0]))
                extracted_title = " ".join(s[1] for s in title_spans).strip()
                if len(extracted_title) > 5:
                    title = extracted_title

        # Fallback for title: first non-empty lines of page 1
        if not title:
            lines = [line.strip() for line in page_1_text.split("\n") if line.strip()]
            for line in lines[:5]:
                if len(line) > 8 and not line.lower().startswith("arxiv") and not line.lower().startswith("doi"):
                    title = line
                    break

        if not title:
            title = "Untitled Research Paper"

        # 3. Extract Abstract
        abstract_patterns = [
            r"(?i)\babstract\b[\s\:\.\-\—]+(.*?)(?=\b(1\.?\s+introduction|i\.\s+introduction|introduction|keywords|1\s+overview)\b)",
            r"(?i)\babstract\b[\s\:\.\-\—]+([\s\S]{100,2000}?)(?=\n\s*\n\s*[A-Z0-9\.\s]{3,20}\n)"
        ]
        for pattern in abstract_patterns:
            match = re.search(pattern, page_1_text, re.DOTALL)
            if match:
                abstract = re.sub(r"\s+", " ", match.group(1)).strip()
                break

        # 4. Extract Publication Year
        year_matches = re.findall(r"\b(19\d{2}|20\d{2})\b", page_1_text[:2000])
        valid_years = [int(y) for y in year_matches if 1950 <= int(y) <= 2030]
        if valid_years:
            year = valid_years[0]

        # 5. Extract Authors if not found in doc metadata
        if not authors and title:
            # Look between title and abstract
            try:
                title_idx = page_1_text.find(title)
                abs_idx = page_1_text.lower().find("abstract")
                if title_idx != -1 and abs_idx != -1 and abs_idx > title_idx:
                    between = page_1_text[title_idx + len(title):abs_idx].strip()
                    between_lines = [l.strip() for l in between.split("\n") if l.strip() and not l.strip().isdigit()]
                    candidates = []
                    for line in between_lines[:4]:
                        # Skip emails or affiliations like @ or university or institute
                        if not any(k in line.lower() for k in ["@", "university", "institute", "department", "college", "school"]):
                            cleaned = re.sub(r"[\d\*\†\‡]", "", line).strip()
                            if cleaned and len(cleaned) < 80:
                                candidates.extend(re.split(r"[,;]|\band\b", cleaned))
                    authors = [c.strip() for c in candidates if len(c.strip()) > 2]
            except Exception:
                pass

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "year": year
        }
