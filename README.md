# Astra-Q Backend

A hybrid RAG + Knowledge Graph backend for answering questions over MOSDAC satellite and Earth-observation data.

## Overview

Astra-Q Backend ingests content from the MOSDAC data portal — static HTML pages, PDF documents, and DOCX files — and powers two complementary query pathways:

- **RAG pipeline** — semantic search over a FAISS vector store built from parsed documents.
- **Knowledge Graph pipeline** — natural-language-to-Cypher querying against a Neo4j graph of satellites, products, parameters, and regions.

A FastAPI chat endpoint selects the appropriate mode (KG, RAG, or both) per question, generates answers via Google Gemini, and persists conversation history to Firebase Firestore.

## Key Features

- Static MOSDAC crawling and document download
- PDF and DOCX parsing with text extraction
- FAISS vector index creation and semantic retrieval
- Neo4j knowledge graph population from extracted metadata
- Natural-language-to-Cypher query generation (LangChain + Gemini)
- Hybrid query routing — KG-only, RAG-only, or both
- FastAPI REST endpoints for chat and thread history
- Firebase Firestore for conversation persistence
- Fallback keyword-based search when semantic retrieval misses

## System Architecture

```
User → FastAPI /api/chat → Route Decider (KG / RAG / BOTH)
                                ├── KG → Neo4j → Gemini → Answer
                                └── RAG → FAISS → Gemini → Answer
                                     └── Built from docs_parsed/
```

## Repository Structure

```
Astra_Q_Backend/
├── backend/
│   ├── main.py                       # FastAPI application
│   ├── api/
│   │   ├── routes/chat.py            # Chat and thread endpoints
│   │   └── router_logic.py           # Query mode routing
│   └── session/
│       └── firebase_session.py       # Firestore persistence
├── kg_pipeline/
│   ├── populate_kg.py                # Neo4j graph population
│   ├── kg_nl_demo.py                 # NL→Cypher query chain
│   ├── queries.py                    # Centralized Cypher templates
│   └── metadata_report.txt           # Extracted page metadata
├── rag_pipeline/
│   ├── retrieve.py                   # RAG retrieval + Gemini answer
│   ├── build_vector_index.py         # FAISS index builder
│   └── faiss_store/                  # Pre-built vector index
├── static_pipeline/
│   ├── crawlers/                     # HTML crawling and doc download
│   ├── parsers/                      # PDF and DOCX parsing
│   ├── utils/                        # File and text utilities
│   └── output/                       # Crawled and parsed artifacts
├── mosdac-scraper/
│   └── scripts/                      # Playwright-based dynamic scraper
├── requirements.txt
└── README.md
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API framework | FastAPI |
| Vector store | FAISS (sentence-transformers/all-MiniLM-L6-v2) |
| Graph database | Neo4j |
| LLM | Google Gemini (gemini-2.5-flash-lite) |
| NL→Cypher | LangChain GraphCypherQAChain |
| Document parsing | pdfplumber, python-docx |
| Session store | Firebase Firestore |
| Crawling | requests, BeautifulSoup, Playwright |

## Setup Instructions

```bash
git clone <repo-url>
cd Astra_Q_Backend
python -m venv .venv
```

Activate the virtual environment:

- **Windows**: `.venv\Scripts\activate`
- **Linux/macOS**: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root or in `kg_pipeline/.env` with the following variables:

```env
GOOGLE_API_KEY=
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
NEO4J_DATABASE=
FIREBASE_SERVICE_ACCOUNT_JSON=
```

For local development you may also set `GOOGLE_APPLICATION_CREDENTIALS` to point to a Firebase service account key file instead of `FIREBASE_SERVICE_ACCOUNT_JSON`.

## Running the Backend

```bash
uvicorn backend.main:app --reload
```

The server starts at `http://localhost:8000`.

## Running the Pipelines

### Build the FAISS vector index (one-time)

```bash
python rag_pipeline/build_vector_index.py
```

### Populate the Neo4j knowledge graph (one-time)

```bash
python kg_pipeline/populate_kg.py
```

### Crawl and parse MOSDAC content

```bash
python main.py
```

Follow the interactive menu to run individual pipeline steps or all steps.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message and receive an answer. Accepts `user_id`, `thread_id`, and `message`. |
| GET | `/api/thread/{thread_id}` | Retrieve conversation history. Requires `user_id` query parameter. |
| GET | `/` | Root health check. Returns `{"message": "Astra-Q backend is running"}`. |

### POST `/api/chat` Request Body

```json
{
  "user_id": "anonymous",
  "thread_id": "default",
  "message": "What rainfall products are available from INSAT-3D?",
  "history": []
}
```

### POST `/api/chat` Response

```json
{
  "answer": "INSAT-3D provides rainfall products...",
  "sources": [
    {
      "source": "KG",
      "content_preview": "",
      "cypher": "MATCH ...",
      "rows": []
    }
  ],
  "mode": "kg"
}
```

## Example Usage

```python
import requests

resp = requests.post("http://localhost:8000/api/chat", json={
    "message": "Which satellites observe sea surface temperature?",
})
print(resp.json()["answer"])
```

```bash
# RAG-only query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain how SST is measured from INSAT-3D"}'
```

## Current Implementation Status

The following components are implemented and functional:

- **Content ingestion**: Static MOSDAC crawling, PDF/DOCX download and parsing, metadata extraction
- **RAG pipeline**: FAISS vector index creation, semantic retrieval, Gemini answer generation, keyword fallback
- **Knowledge Graph**: Neo4j schema (Satellite, Product, Parameter, Region), graph population from metadata, NL→Cypher querying
- **API**: FastAPI chat endpoint with hybrid KG/RAG/BOTH routing, Firebase conversation persistence
- **Utilities**: File I/O helpers, text cleaning, schema definitions
