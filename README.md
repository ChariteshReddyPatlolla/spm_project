# Multi-Paper Research Assistant – Agentic RAG System

A production-quality, local-first Multi-Paper Research Assistant built with FastAPI, LangGraph, ChromaDB, BM25+, Cross-Encoder reranking, and React + Tailwind CSS. Designed to ingest academic papers, perform hybrid retrieval and comparative analysis across 9 dimensions, validate citations with zero hallucinations, and maintain multi-turn research conversations.

---

## 🏛 Architecture Overview

```
                                      +-----------------------------+
                                      |     React + Tailwind UI     |
                                      +--------------+--------------+
                                                     | Axios / REST
                                                     v
                                      +-----------------------------+
                                      |     FastAPI Backend API     |
                                      +--------------+--------------+
                                                     |
         +-------------------------------------------+-------------------------------------------+
         |                                           |                                           |
         v                                           v                                           v
+------------------+                        +------------------+                        +------------------+
| Ingestion Engine |                        | Agentic RAG Core |                        | Research Memory  |
| - PyMuPDF / OCR  |                        | - LangGraph Node |                        | - SQLite DB      |
| - Header cleaner |                        | - Dense Embed    |                        | - Rolling Context|
| - Table markdown |                        | - BM25+ / RRF    |                        | - Pronoun/Deictic|
| - Section chunks |                        | - Cross-Encoder  |                        |   Resolution     |
+--------+---------+                        +--------+---------+                        +--------+---------+
         | Chunks & Vectors                          | Evidence & Citations                      | History
         v                                           v                                           v
+------------------+                        +------------------+                        +------------------+
| ChromaDB Storage |                        | Citation Validator|                       | SQLite Sessions  |
| (Dense Vectors)  |                        | [Paper, Page X]  |                        | & Summaries      |
+------------------+                        +------------------+                        +------------------+
```

---

## 🚀 Key Features by Priority

### Priority 1: Multi-Paper PDF Ingestion
- **Simultaneous Uploads:** Process multiple academic papers concurrently.
- **Robust Extraction:** Uses `PyMuPDF` with layout heuristics for 2-column papers, table extraction into Markdown, and `pytesseract` OCR fallback for scanned figures and documents.
- **Header/Footer Removal:** Automatically scrubs running headers, footers, and page numbers from body content while preserving document structure.
- **Deduplication:** SHA-256 fingerprinting prevents redundant processing.
- **Cascade Deletion:** Paper removal deletes all associated pages, chunks, ChromaDB vector embeddings, summaries, and comparative analyses.

### Priority 2: Modular Hybrid RAG Pipeline
- **Structure-Aware Chunking:** Segments text by section headings (`Introduction`, `Methodology`, etc.) with configurable size and token overlap, tracking exact page numbers and chunk IDs.
- **Dense Embeddings:** Hugging Face 384-dimensional dense semantic representations with LRU caching.
- **ChromaDB Vector Database:** Persistent storage with document ID and page filtering.
- **BM25+ Keyword Retrieval:** Exact keyword matching resistant to term frequency saturation on short corpora.
- **Reciprocal Rank Fusion (RRF):** Merges dense semantic and BM25+ lexical candidate ranks.
- **Cross-Encoder Reranking:** Computes cross-attention relevance scores to surface the most contextually relevant passages.

### Priority 3: Source Attribution & Citation Reliability
- **Strict Format:** Every factual assertion is attributed with `[Paper Title, Page X]`.
- **Ground-Truth Validation:** The `citation_validator` matches citations against retrieved chunks, verifying that the claimed text and page number actually appear in the source.
- **Zero Hallucination:** If evidence is missing, the system explicitly responds: *"The uploaded documents do not contain evidence regarding..."*
- **Interactive Citation Drawer:** Clicking any citation badge opens a drawer showing the ground-truth supporting passage, exact page number, and direct link to the uploaded PDF.

### Priority 4: Multi-Paper Comparative Analysis
- **9 Core Dimensions:**
  1. Research Objectives
  2. Research Problems & Gaps
  3. Methodologies
  4. Proposed Architectures & Algorithms
  5. Datasets & Dataset Sizes
  6. Evaluation Metrics
  7. Experimental Results
  8. Limitations
  9. Future Research Directions
- **Safeguards:** Explicitly marks *"Not reported in paper"* whenever a paper omits specific metrics or experimental values.

### Priority 5: LangGraph Agentic Research Workflow
- **Dynamic State Graph:** Implemented using `langgraph.graph.StateGraph` with conditional routing across 9 specialized nodes:
  - `Query Understanding`
  - `Research Planning`
  - `Subtask Generation`
  - `Document Retrieval`
  - `Evidence Extraction`
  - `Multi-Paper Analysis`
  - `Answer Synthesis`
  - `Citation Validation`
  - `Final Response`
- **Contradiction Detection:** Surfaces conflicting experimental results or opposing methodology paradigms across papers.

### Priority 6: Structured Academic Summarization
- Automatically extracts 11 structured fields for each paper and caches the result in SQLite:
  - Title & Authors, Research Objective, Problem Statement, Methodology, Architecture, Algorithms, Datasets, Metrics, Results, Contributions, Limitations, Future Work.

### Priority 7: Conversational Memory & Sessions
- **Session Isolation:** Manages distinct research sessions stored in SQLite.
- **Pronoun & Deictic Resolution:** Resolves conversational references like *"the first paper"*, *"that methodology"*, or *"compare both"* using paper titles from the session context.
- **Rolling Summaries:** Compresses prior dialogue to maintain context without exceeding token windows.

---

## 🛠 Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Axios, Lucide React |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn |
| **AI / RAG** | LangGraph, ChromaDB, BM25+ (`rank_bm25`), Sentence Transformers, Ollama |
| **PDF / OCR** | PyMuPDF (`fitz`), pdfplumber, Tesseract OCR (`pytesseract`) |
| **Storage** | SQLite (`research_assistant.db`), Local Chroma vector index |

---

## 📂 Project Structure

```
spm_project/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph state graph and research nodes
│   │   ├── api/v1/          # FastAPI routers (documents, chat, comparative, summary)
│   │   ├── core/            # Config, logging, directory paths
│   │   ├── database/        # SQLite models and connection setup
│   │   ├── embeddings/      # Dense embedding service and ChromaDB vector store
│   │   ├── ingestion/       # PyMuPDF parser, OCR fallback, metadata extractor
│   │   ├── retrieval/       # Chunker, BM25+ retriever, Cross-Encoder reranker
│   │   ├── schemas/         # Pydantic v2 validation models
│   │   ├── services/        # LLM client, citation validator, comparative service
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # Pytest suite covering all 10 phases
│   ├── Dockerfile           # Backend containerization
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Badges, drawer, comparison table, sidebar, navbar
│   │   ├── context/         # ResearchContext global state
│   │   ├── pages/           # Dashboard, DocumentLibrary, Chat, Comparative, Summaries
│   │   ├── services/        # Axios API client
│   │   ├── App.jsx          # Route configuration
│   │   └── main.jsx         # React DOM mounting
│   ├── Dockerfile           # Multi-stage Nginx containerization
│   └── package.json         # Node.js dependencies
├── storage/
│   ├── chroma/              # Persistent ChromaDB vector indices
│   ├── data/                # SQLite database (research_assistant.db)
│   └── uploads/             # Ingested PDF documents
├── sample_papers/           # Synthetic benchmarking research papers
├── docker-compose.yml       # Complete multi-container orchestration
└── README.md                # System documentation
```

---

## ⚡ Quick Start (Local Setup)

### 🚀 Windows One-Click Launch
If you are on Windows, simply run or double-click **`start.bat`** in the root directory:
```bat
start.bat
```
This automatically launches the FastAPI backend, the React frontend, and opens [http://localhost:5173](http://localhost:5173) in your default browser.

### Manual Setup

#### Prerequisites
- Python 3.11 (`uv` or `python` venv)
- Node.js 18+ & npm
- (Optional) [Ollama](https://ollama.com/) with `llama3` pulled (`ollama pull llama3`)

### 1. Backend Setup

```bash
# Navigate to backend and create virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at: `http://localhost:8000`  
Swagger API Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend UI will be available at: `http://localhost:5173`

---

## 🐳 Docker Deployment

To launch the complete system (Ollama + Backend + Frontend) using Docker:

```bash
docker-compose up --build -d
```

- **Frontend UI:** `http://localhost:3000`
- **FastAPI Documentation:** `http://localhost:8000/docs`
- **Ollama API:** `http://localhost:11434`

---

## 🧪 Running the Test Suite

Execute the complete end-to-end test suite:

```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests -v -c backend/pytest.ini
```

Verified tests include:
- `test_chunker.py`: Text cleaning, hyphenation removal, heading detection, page preservation.
- `test_ingestion.py`: PyMuPDF layout extraction, table extraction, metadata heuristics.
- `test_retrieval.py`: BM25+ scoring, cross-encoder ranking, Reciprocal Rank Fusion.
- `test_citations.py`: Citation formatting `[Paper, Page X]` and strict ground-truth verification.
- `test_agent.py`: LangGraph multi-node state graph workflow execution.
- `test_comparative.py`: 9-dimension comparative analysis matrix.
- `test_summarization.py`: 11-dimension academic paper summarization and caching.
- `test_api.py`: Full API lifecycle (document upload, listing, chat querying, summarization, cascade deletion).

---

## 📡 API Reference Summary

- `GET /api/v1/status`: Health check and system statistics.
- `POST /api/v1/documents/upload`: Multipart upload for multiple PDFs.
- `GET /api/v1/documents`: List all uploaded papers with extraction metadata.
- `GET /api/v1/documents/{doc_id}`: Retrieve detailed metadata and chunk distribution.
- `DELETE /api/v1/documents/{doc_id}`: Cascade delete paper, chunks, and vector embeddings.
- `POST /api/v1/chat`: Ask research questions with agentic workflow and citation verification.
- `POST /api/v1/comparative`: Generate 9-dimension comparative analysis across selected papers.
- `POST /api/v1/summary`: Retrieve or generate 11-dimension paper summary.
- `GET /api/v1/sessions`: List conversational research sessions.

