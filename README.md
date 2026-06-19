# Vanta AI

> Hybrid RAG + Knowledge Graph backend for traceable domain question answering, designed to evolve into an agentic knowledge system.

Vanta AI ingests content from satellite data portals (MOSDAC), builds a FAISS vector store and a Neo4j knowledge graph, and powers two complementary query pathways — semantic retrieval and graph-based reasoning — via a FastAPI chat API backed by Google Gemini and Firebase Firestore.

## Current Capabilities

- **Content ingestion**: Static HTML crawling, PDF/DOCX download and parsing, metadata extraction
- **RAG pipeline**: FAISS vector index (all-MiniLM-L6-v2), semantic retrieval, Gemini 2.5 Flash-lite answer generation, keyword fallback
- **Knowledge Graph**: Neo4j schema (Satellite, Product, Parameter, Region), graph population from metadata, NL→Cypher querying via LangChain
- **Hybrid routing**: Per-query mode selection (KG, RAG, or both) with simple keyword heuristics
- **Session persistence**: Firebase Firestore for conversation history
- **Configurable CORS**: Origins read from `CORS_ALLOWED_ORIGINS` env var

## Architecture

```
User → FastAPI /api/chat → Route Decider (KG / RAG / BOTH)
                                ├── KG → Neo4j → Gemini → Answer
                                └── RAG → FAISS → Gemini → Answer
                                     └── Built from docs_parsed/
```

## Repository Structure

```
vanta-ai/
├── backend/
│   ├── main.py                       # FastAPI application (lazy Firebase init)
│   ├── api/
│   │   ├── routes/chat.py            # Chat and thread endpoints
│   │   └── router_logic.py           # Query mode routing
│   └── session/
│       └── firebase_session.py       # Firestore persistence
├── core/
│   └── config.py                     # Centralized configuration
├── kg_pipeline/
│   ├── populate_kg.py                # Neo4j graph population
│   ├── kg_nl_demo.py                 # NL→Cypher query chain (lazy init)
│   ├── queries.py                    # Centralized Cypher templates
│   └── metadata_report.txt           # Extracted page metadata
├── rag_pipeline/
│   ├── retrieve.py                   # RAG retrieval + Gemini answer (lazy init)
│   ├── build_vector_index.py         # FAISS index builder
│   └── faiss_store/                  # Pre-built vector index (generated, not tracked)
├── static_pipeline/
│   ├── crawlers/                     # HTML crawling and doc download
│   ├── parsers/                      # PDF and DOCX parsing
│   └── utils/                        # File and text utilities
├── scripts/
│   ├── run_pipeline.py               # Pipeline step runner
│   ├── run_rag_cli.py                # Interactive RAG demo
│   └── lambda_function.py            # AWS Lambda scraper (legacy)
├── mosdac-scraper/
│   └── scripts/                      # Playwright-based dynamic scraper
├── core/
│   └── config.py                     # Centralized env config
├── .env.example                      # Environment template
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

## Setup

```bash
git clone <repo-url>
cd vanta-ai
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
cp .env.example .env        # Edit .env with your credentials
pip install -r requirements.txt
```

## Environment Variables

See `.env.example` for all required variables. Key ones:

- `GOOGLE_API_KEY` — Gemini API key
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — Neo4j connection
- `FIREBASE_SERVICE_ACCOUNT_JSON` or `GOOGLE_APPLICATION_CREDENTIALS` — Firebase auth
- `CORS_ALLOWED_ORIGINS` — comma-separated origin list (default: `http://localhost:5173,http://localhost:5174`)

## Running

```bash
uvicorn backend.main:app --reload
```

Open `http://localhost:8000` for health check.

### One-time pipelines

```bash
python rag_pipeline/build_vector_index.py   # Build FAISS index
python kg_pipeline/populate_kg.py            # Populate Neo4j graph
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message. Returns answer with sources and mode. |
| GET | `/api/thread/{thread_id}` | Get conversation history. Requires `user_id` query param. |
| GET | `/` | Health check. |

## Known Limitations

- Route decider uses simple keyword matching (will evolve into an intent classifier)
- No grounding verifier — hallucination detection is not yet implemented
- No structured traces per request
- No evaluation benchmarks or test suite
- No Docker image or CI pipeline
- spaCy model `en_core_web_sm` must be downloaded separately (`python -m spacy download en_core_web_sm`)

## Roadmap

- **Tool registry**: `Planner` + `Executor` pattern for extensible tool use
- **Agent planner**: Intent classification → plan → execute → synthesize
- **Grounding verifier**: Citation validation and hallucination detection
- **Structured traces**: Per-request observability (steps, evidence, confidence)
- **Evaluation benchmarks**: Gold Q/A datasets, retrieval MRR, routing accuracy
- **MCP integration**: Out-of-process tool boundaries (later, not first)
