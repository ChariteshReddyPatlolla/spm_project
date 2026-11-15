import requests

test_suite = [
    ("Part 3 QA", "what is the main objective and methodology of the uploaded research papers?"),
    ("Part 3 QA Single", "what is the main objective of Transformer"),
    ("Part 5 Conversational", "What papers do I have?"),
    ("Part 5 Fullform", "What is the full form of BERT?"),
    ("Part 5 Summary", "give me the summary of papers"),
    ("Part 6 Followup", "Explain the methodology of the second paper in more detail.")
]

sess_res = requests.post("http://127.0.0.1:8000/api/v1/sessions", json={"title": "Presentation Demo Session"})
sess_id = sess_res.json().get("id")
print(f"Created Presentation Demo Session: {sess_id}\n")

for label, query in test_suite:
    payload = {
        "query": query,
        "session_id": sess_id,
        "use_agentic_workflow": True
    }
    r = requests.post("http://127.0.0.1:8000/api/v1/chat", json=payload)
    data = r.json()
    first_line = data.get("content", "").split("\n")[0]
    c_count = len(data.get("citations", []))
    print(f"[{label}] Query: '{query}'")
    print(f"   Output: {first_line[:95]}")
    print(f"   Citations: {c_count}")
    print(f"   Steps: {[s.get('step_name') for s in data.get('agent_steps', [])]}\n")
