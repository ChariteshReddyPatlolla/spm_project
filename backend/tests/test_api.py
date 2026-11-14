import os
import pytest
from backend.app.database.models import Document

def test_api_system_status(client):
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "documents_indexed" in data

def test_api_upload_documents(client):
    pdf_path = "sample_papers/attention_paper.pdf"
    with open(pdf_path, "rb") as f:
        files = [("files", ("attention_paper.pdf", f.read(), "application/pdf"))]

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 1
    doc_id = docs[0]["id"]
    assert doc_id is not None
    assert docs[0]["status"] == "ready"

    # List documents
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    assert any(d["id"] == doc_id for d in list_res.json())

    # Get single document detail
    detail_res = client.get(f"/api/v1/documents/{doc_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["total_chunks"] > 0

    # Chat endpoint
    chat_payload = {
        "query": "What BLEU score did Transformer achieve on WMT 2014?",
        "selected_document_ids": [doc_id],
        "use_agentic_workflow": True
    }
    chat_res = client.post("/api/v1/chat", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "content" in chat_data
    assert len(chat_data["citations"]) > 0
    assert len(chat_data["agent_steps"]) > 0

    # Summary endpoint
    summary_res = client.post("/api/v1/summary", json={"document_id": doc_id})
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert len(summary_data["methodology"]) > 0

    # Delete paper
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 204

    # Confirm deleted
    assert client.get(f"/api/v1/documents/{doc_id}").status_code == 404

