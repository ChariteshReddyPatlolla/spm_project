import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

queries = [
    "what is the fullform of BERT",
    "what are the papers i have now",
    "what are you saying",
    "hi"
]

print("=" * 80)
print("TESTING EXACT SCREENSHOT QUERIES ON RUNNING BACKEND")
print("=" * 80)

for q in queries:
    print(f"\n[QUERY]: \"{q}\"")
    res = requests.post(f"{BASE_URL}/chat", json={"query": q, "use_agentic_workflow": True})
    assert res.status_code == 200, f"Failed with {res.status_code}: {res.text}"
    data = res.json()
    print("[RESPONSE]:")
    print(data.get("content"))
    print(f"[CITATIONS]: {len(data.get('citations', []))}")
    print("-" * 80)

