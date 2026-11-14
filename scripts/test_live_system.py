import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_section("1. System Health Check")
    res = requests.get(f"{BASE_URL}/status")
    assert res.status_code == 200, f"Status failed: {res.text}"
    status_data = res.json()
    print("System Status:", json.dumps(status_data, indent=2))

    print_section("2. Upload Sample Papers (Attention & BERT)")
    files = [
        ("files", ("attention_paper.pdf", open("sample_papers/attention_paper.pdf", "rb"), "application/pdf")),
        ("files", ("bert_paper.pdf", open("sample_papers/bert_paper.pdf", "rb"), "application/pdf"))
    ]
    res = requests.post(f"{BASE_URL}/documents/upload", files=files)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    uploaded_docs = res.json()
    print(f"Successfully uploaded {len(uploaded_docs)} documents:")
    doc_ids = []
    for d in uploaded_docs:
        doc_ids.append(d["id"])
        print(f" - [{d['id'][:8]}] {d['title']} ({d['page_count']} pages, Status: {d['status']})")
        print(f"   Authors: {', '.join(d['authors'])}")

    print_section("3. List and Verify Ingested Documents")
    res = requests.get(f"{BASE_URL}/documents")
    assert res.status_code == 200
    docs = res.json()
    print(f"Total documents in database: {len(docs)}")
    for d in docs:
        detail_res = requests.get(f"{BASE_URL}/documents/{d['id']}")
        detail = detail_res.json()
        print(f" - {detail['title']} | Chunks: {detail['total_chunks']} | Pages: {detail['page_count']}")

    print_section("4. Structured Academic Paper Summarization (11 Dimensions)")
    target_doc_id = doc_ids[0]
    res = requests.post(f"{BASE_URL}/summary", json={"document_id": target_doc_id})
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary = res.json()
    print(f"Paper: {summary['title']}")
    print(f"Research Objective: {summary['research_objective'][:150]}...")
    print(f"Methodology: {summary['methodology'][:150]}...")
    print(f"Proposed Architecture: {summary['proposed_architecture'][:150]}...")
    print(f"Evaluation Metrics: {summary['evaluation_metrics'][:150]}...")
    print(f"Experimental Results: {summary['experimental_results'][:150]}...")
    print(f"Citations Extracted: {len(summary['citations'])}")
    for c in summary['citations'][:3]:
        print(f"   * [{c['paper_title']}, Page {c['page_number']}] - {c['snippet'][:80]}...")

    print_section("5. Multi-Paper Comparative Analysis (9 Dimensions)")
    res = requests.post(f"{BASE_URL}/comparative", json={"document_ids": doc_ids})
    assert res.status_code == 200, f"Comparative analysis failed: {res.text}"
    comp = res.json()
    print(f"Comparison Title: {comp['title']}")
    print(f"\nStructured Comparison Matrix ({len(comp['comparison_table'])} aspects):")
    for row in comp['comparison_table'][:5]:
        print(f" * {row['aspect']}:")
        for p_id, val in row['values'].items():
            paper_name = comp['paper_titles'].get(p_id, p_id)
            print(f"     - {paper_name[:25]}: {val[:80]}...")
    
    print("\nAdvantages & Disadvantages:")
    for adv in comp['advantages_disadvantages']:
        print(f" * {adv['paper_title']}:")
        print(f"     Advantages: {adv['advantages'][:2]}")
        print(f"     Disadvantages: {adv['disadvantages'][:2]}")

    print_section("6. Conversational Agentic Chat (Turn 1: Factual Query)")
    chat_payload = {
        "query": "What BLEU score did the Transformer achieve on English-to-German?",
        "selected_document_ids": doc_ids,
        "use_agentic_workflow": True
    }
    res = requests.post(f"{BASE_URL}/chat", json=chat_payload)
    assert res.status_code == 200, f"Chat failed: {res.text}"
    chat_turn1 = res.json()
    session_id = chat_turn1["session_id"]
    print(f"Session ID: {session_id}")
    print(f"Agent Steps Executed ({len(chat_turn1['agent_steps'])}):")
    for step in chat_turn1['agent_steps']:
        print(f" - [{step['step_name']}] {step['description']}")
    print("\nAnswer Content:")
    print(chat_turn1["content"])
    print(f"\nValidated Citations ({len(chat_turn1['citations'])}):")
    for c in chat_turn1["citations"]:
        print(f" - [{c['paper_title']}, Page {c['page_number']}] (Grounding verified: {c['is_validated']})")
        print(f"   Evidence: {c['snippet']}")

    print_section("7. Conversational Agentic Chat (Turn 2: Follow-up & Pronoun Resolution)")
    chat_payload2 = {
        "session_id": session_id,
        "query": "Compare the first paper with BERT on their training datasets.",
        "selected_document_ids": doc_ids,
        "use_agentic_workflow": True
    }
    res = requests.post(f"{BASE_URL}/chat", json=chat_payload2)
    assert res.status_code == 200, f"Turn 2 failed: {res.text}"
    chat_turn2 = res.json()
    print("\nTurn 2 Answer Content:")
    print(chat_turn2["content"])
    print(f"\nTurn 2 Validated Citations ({len(chat_turn2['citations'])}):")
    for c in chat_turn2["citations"]:
        print(f" - [{c['paper_title']}, Page {c['page_number']}]")

    print_section("8. Conversational Session History & Rolling Summary")
    res = requests.get(f"{BASE_URL}/sessions/{session_id}")
    assert res.status_code == 200
    sess = res.json()
    print(f"Session Title: {sess['title']}")
    print(f"Total Messages: {len(sess['messages'])}")
    print(f"Rolling Summary: {sess['rolling_summary']}")

    print("\n" + "=" * 70)
    print("  ALL LIVE INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()

