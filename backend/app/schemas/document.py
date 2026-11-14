from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PageInfo(BaseModel):
    page_number: int
    text_preview: str
    has_images: bool = False
    has_tables: bool = False
    is_ocr: bool = False

class DocumentBase(BaseModel):
    filename: str
    title: str = "Untitled Document"
    authors: List[str] = Field(default_factory=list)
    abstract: str = ""
    year: Optional[int] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: str
    file_path: str
    file_hash: str
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    pages: Optional[List[PageInfo]] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentDetail(DocumentResponse):
    total_chunks: int = 0
