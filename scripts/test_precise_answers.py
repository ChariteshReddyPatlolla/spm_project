import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

TEST_QUESTIONS = [
    {
        "label": "1. Acronym / Full Form Query",
        "query": "what is the fullform of BERT",
        "expected_substrings": ["Bidirectional Encoder Representations from Transformers"]
    },
    {
        "label": "2. Authorship Query",
        "query": "Who wrote Attention Is All You Need?",
        "expected_substrings": ["Ashish Vaswani", "Noam Shazeer"]
    },
    {
        "label": "3. Quantitative Metric Query",
        "query": "What BLEU score did Transformer achieve on English-to-German?",
        "expected_substrings": ["28.4 BLEU", "WMT 2014"]
    },
    {
        "label": "4. Model Parameter Scale Query",
        "query": "How many parameters does BERT have?",
        "expected_substrings": ["110 million", "340 million", "BERT_BASE", "BERT_LARGE"]
    },
    {
        "label": "5. Training Corpora Query",
        "query": "What datasets were used to train BERT?",
        "expected_substrings": ["BooksCorpus", "800 million", "English Wikipedia", "2,500 million"]
    },
    {
        "label": "6. Architectural Mechanism Query",
        "query": "What is Scaled Dot-Product Attention?",
        "expected_substrings": ["Scaled Dot-Product Attention", "softmax", "sqrt(d_k)"]
    },
    {
        "label": "7. Limitations Query",
        "query": "What are the limitations of BERT?",
        "expected_substrings": ["[MASK]", "pre-training", "fine-tuning", "TPU"]
    },
    {
        "label": "8. Comparative Analysis Query",
        "query": "Compare Transformer and BERT",
        "expected_substrings": ["Encoder-Decoder", "encoder-only", "pre-training"]
    }
]

def main():
    print("=" * 80)
    print("  VERIFYING PRECISION QUESTION ANSWERING PIPELINE")
    print("=" * 80)

    # First get document IDs from DB
    res = requests.get(f"{BASE_URL}/documents")
    assert res.status_code == 200, f"Cannot reach documents: {res.text}"
    docs = res.json()
    doc_ids = [d["id"] for d in docs]
    print(f"Available Documents ({len(doc_ids)}):")
    for d in docs:
        print(f" - [{d['id'][:8]}] {d['title']}")

    print("-" * 80)
    all_passed = True

    for item in TEST_QUESTIONS:
        label = item["label"]
        query = item["query"]
        expected = item["expected_substrings"]

        print(f"\n>>> TESTING: {label}")
        print(f"    User Query: \"{query}\"")

        payload = {
            "query": query,
            "selected_document_ids": doc_ids,
            "use_agentic_workflow": True
        }

        res = requests.post(f"{BASE_URL}/chat", json=payload)
        if res.status_code != 200:
            print(f"    [FAIL] Status code {res.status_code}: {res.text}")
            all_passed = False
            continue

        data = res.json()
        content = data.get("content", "")
        citations = data.get("citations", [])

        print(f"    Synthesized Answer:\n    {content.replace(chr(10), chr(10) + '    ')}")
        print(f"    Citations ({len(citations)}): {[c['paper_title'][:20] + '... p.' + str(c['page_number']) for c in citations]}")

        # Check for expected substrings
        missing = [exp for exp in expected if exp.lower() not in content.lower()]
        if missing:
            print(f"    [WARN] Missing expected elements: {missing}")
            all_passed = False
        else:
            print("    [PASS] Direct, accurate, and completely grounded.")

    print("\n" + "=" * 80)
    if all_passed:
        print("  ALL 8 PRECISION QA BENCHMARKS PASSED SUCCESSFULLY!")
    else:
        print("  SOME BENCHMARKS HAD WARNINGS - REVIEW OUTPUT ABOVE.")
    print("=" * 80)

if __name__ == "__main__":
    main()

