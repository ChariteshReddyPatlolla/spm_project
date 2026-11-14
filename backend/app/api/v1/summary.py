from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.summary import SummaryRequest, PaperSummaryResponse
from backend.app.services.summarization_service import summarization_service

router = APIRouter(prefix="/summary", tags=["Paper Summarization"])

@router.post("", response_model=PaperSummaryResponse)
def generate_summary(request: SummaryRequest, db: Session = Depends(get_db)):
    """
    Generate or retrieve cached structured summary for a research paper.
    Contains all 11 required dimensions and page-level citations.
    """
    try:
        response = summarization_service.get_or_generate_summary(
            document_id=request.document_id,
            db=db,
            regenerate=request.regenerate
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=PaperSummaryResponse)
def get_summary(document_id: str, db: Session = Depends(get_db)):
    """Get structured summary for document."""
    try:
        response = summarization_service.get_or_generate_summary(
            document_id=document_id,
            db=db,
            regenerate=False
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

