import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import ComparisonAnalysis, Document
from backend.app.schemas.comparative import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    ComparisonRow,
    AdvantageDisadvantage
)
from backend.app.schemas.chat import Citation
from backend.app.services.comparative_service import comparative_service

router = APIRouter(prefix="/comparative", tags=["Comparative Analysis"])

@router.post("", response_model=ComparativeAnalysisResponse)
def run_comparison(
    request: ComparativeAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Run multi-paper comparative analysis comparing 9 core dimensions:
    objectives, gaps, methodologies, architectures, datasets, metrics, results, limitations, future work.
    """
    if not request.document_ids or len(request.document_ids) < 1:
        raise HTTPException(status_code=400, detail="At least one paper must be selected for comparison.")

    try:
        response = comparative_service.analyze_papers(
            document_ids=request.document_ids,
            db=db,
            custom_aspects=request.custom_aspects
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ComparativeAnalysisResponse])
def list_comparisons(db: Session = Depends(get_db)):
    """List historical comparative analyses."""
    analyses = db.query(ComparisonAnalysis).order_by(ComparisonAnalysis.created_at.desc()).all()
    results = []
    for a in analyses:
        doc_ids = json.loads(a.document_ids or "[]")
        docs = db.query(Document).filter(Document.id.in_(doc_ids)).all() if doc_ids else []
        paper_titles = {d.id: d.title for d in docs}
        rows = [ComparisonRow(**r) for r in json.loads(a.comparison_table or "[]")]
        adv_dis = [AdvantageDisadvantage(**ad) for ad in json.loads(a.advantages_disadvantages or "[]")]
        cits = [Citation(**c) for c in json.loads(a.citations or "[]")]

        results.append(ComparativeAnalysisResponse(
            id=a.id,
            title=a.title,
            document_ids=doc_ids,
            paper_titles=paper_titles,
            comparison_table=rows,
            detailed_analysis=a.detailed_analysis,
            advantages_disadvantages=adv_dis,
            research_gaps=a.research_gaps or "",
            citations=cits,
            created_at=a.created_at
        ))
    return results

@router.get("/{analysis_id}", response_model=ComparativeAnalysisResponse)
def get_comparison(analysis_id: str, db: Session = Depends(get_db)):
    """Get single comparative analysis by ID."""
    a = db.query(ComparisonAnalysis).filter(ComparisonAnalysis.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Comparison analysis not found.")

    doc_ids = json.loads(a.document_ids or "[]")
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all() if doc_ids else []
    paper_titles = {d.id: d.title for d in docs}
    rows = [ComparisonRow(**r) for r in json.loads(a.comparison_table or "[]")]
    adv_dis = [AdvantageDisadvantage(**ad) for ad in json.loads(a.advantages_disadvantages or "[]")]
    cits = [Citation(**c) for c in json.loads(a.citations or "[]")]

    return ComparativeAnalysisResponse(
        id=a.id,
        title=a.title,
        document_ids=doc_ids,
        paper_titles=paper_titles,
        comparison_table=rows,
        detailed_analysis=a.detailed_analysis,
        advantages_disadvantages=adv_dis,
        research_gaps=a.research_gaps or "",
        citations=cits,
        created_at=a.created_at
    )

