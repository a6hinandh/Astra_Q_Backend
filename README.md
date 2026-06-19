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
                                ├── ToolRegistry
                                │   ├── knowledge_graph → Neo4j → Gemini → Answer
                                │   └── vector_search  → FAISS → Gemini → Answer
                                └── Both tools combined
```

## Repository Structure

```
vanta-ai/
├── backend/
│   ├── main.py                       # FastAPI application (lazy Firebase init)
│   ├── api/
│   │   ├── routes/chat.py            # Chat and thread endpoints → calls ToolRegistry
│   │   └── router_logic.py           # Query mode routing
│   └── session/
│       └── firebase_session.py       # Firestore persistence
├── core/
│   ├── config.py                     # Centralized configuration
│   ├── models.py                     # Shared models (Evidence, ToolResult, etc.)
│   └── tracing.py                    # Trace models, TraceStore, generate_trace_id
├── tools/
│   ├── __init__.py                   # get_default_registry() factory
│   ├── base.py                       # BaseTool interface
│   ├── registry.py                   # ToolRegistry (register, get, list, run)
│   ├── vector_search.py              # VectorSearchTool → rag_pipeline/retrieve.py
│   └── knowledge_graph.py            # KnowledgeGraphTool → kg_pipeline/kg_nl_demo.py
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
├── tests/
│   ├── test_config.py                # Config tests (Day 1-2)
│   ├── test_imports.py               # Import safety tests (Day 1-2)
│   ├── test_tool_registry.py         # Registry tests (Day 3-4)
│   ├── test_tool_contracts.py        # Tool model contract tests (Day 3-4)
│   ├── test_default_registry.py      # Default registry smoke tests (Day 3-4)
│   ├── test_tracing_models.py       # Trace model tests (Day 5-6)
│   ├── test_trace_store.py          # TraceStore tests (Day 5-6)
│   └── test_tool_registry_tracing.py # Registry tracing tests (Day 5-6)
├── mosdac-scraper/
│   └── scripts/                      # Playwright-based dynamic scraper
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
| POST | `/api/chat` | Send a message. Returns answer, sources, mode, and trace_id. |
| GET | `/api/thread/{thread_id}` | Get conversation history. Requires `user_id` query param. |
| GET | `/api/trace/{trace_id}` | Get structured trace for a past request. |
| GET | `/api/traces/recent?limit=20` | List recent traces. |
| GET | `/` | Health check. |

## Tool Layer

Vanta AI now wraps retrieval and knowledge graph capabilities behind clean tool interfaces. This prepares the repo for the future agent planner, structured traces, evaluation, and MCP integration.

### Current tools

| Tool | Description | Backend |
|------|-------------|---------|
| `vector_search` | Semantic search over FAISS vector store with Gemini answer generation | `rag_pipeline/retrieve.py` |
| `knowledge_graph` | NL→Cypher querying over Neo4j knowledge graph | `kg_pipeline/kg_nl_demo.py` |

### Usage

```python
from tools import get_default_registry

registry = get_default_registry()
# No external connections at import time — tools are just lightweight wrappers

result = registry.run_tool("vector_search", "What is INSAT-3D resolution?")
# Or:
result = registry.run_tool("knowledge_graph", "Which products are ocean-related from Oceansat-3?")

print(result.success, result.metadata.get("answer"))
```

### Design

- `BaseTool` (ABC) in `tools/base.py` defines the interface: `name`, `description`, `input_schema`, `run(input: ToolInput) -> ToolResult`.
- `ToolRegistry` in `tools/registry.py` manages registration, lookup, and execution. Duplicate names raise `DuplicateToolError`; missing names raise `ToolNotFoundError`.
- `get_default_registry()` in `tools/__init__.py` creates a pre-configured registry with both tools. Calling it does **not** connect to Neo4j, load FAISS, call Gemini, or require Firebase.
- Tools use lazy imports and graceful error handling — missing dependencies or unconfigured services return a controlled `ToolResult` error instead of crashing.
- The chat endpoint (`backend/api/routes/chat.py`) now routes queries through the `ToolRegistry`, preserving the existing response shape.
- Every tool run is traced with latency, success/error, and evidence count when called through the registry with a trace object.
- MCP integration is intentionally deferred until tool boundaries are stable.

## Structured Tracing

Every chat request now receives a `trace_id`. Tool calls are traced with latency, success/error, and evidence counts. Traces make the system easier to debug and prepare it for future planner/router workflows.

### How it works

1. When a `POST /api/chat` request arrives, a `RequestTrace` is created with a unique `trace_id`, `user_id`, `thread_id`, and `query`.
2. The selected mode is recorded.
3. Each tool call via the `ToolRegistry` records a `ToolTrace` event on the request trace, capturing `tool_name`, `success`, `evidence_count`, `latency_ms`, and any error.
4. After the response is built, the trace is finalized with `status` (success / error / partial), `final_answer_preview`, and `latency_ms`.
5. The trace is stored in the in-memory `TraceStore` (bounded to the latest 500 traces).
6. The response includes the `trace_id` for later retrieval.

### Retrieving traces

```bash
# Get a specific trace
curl http://localhost:8000/api/trace/<trace_id>

# List recent traces
curl http://localhost:8000/api/traces/recent?limit=10
```

### Design

- Tracing is **optional** at the registry level — `registry.run_tool()` accepts an optional `trace` parameter. Callers that don't pass a trace work identically to before.
- No secrets, API keys, or full document chunks are stored in traces. Query text is previewed (first 100 chars), answers are previewed (first 200 chars).
- The current `TraceStore` is in-memory only, suitable for local and demo use. Production storage is a future improvement.
- Request-level logging uses Python's `logging` module (not `print`). Log lines include `trace_id`, `mode`, and `status`.

### Trace data model

```
RequestTrace
├── trace_id, user_id, thread_id, query
├── selected_mode, status, latency_ms
├── final_answer_preview, error
└── tool_traces[]
    ├── tool_name, input_summary, success
    ├── evidence_count, latency_ms, error
    └── metadata
```

## Known Limitations

- Route decider uses simple keyword matching (will evolve into an intent classifier)
- No grounding verifier — hallucination detection is not yet implemented
- No evaluation benchmarks or test suite
- No Docker image or CI pipeline
- spaCy model `en_core_web_sm` must be downloaded separately (`python -m spacy download en_core_web_sm`)
- Trace storage is in-memory only (not persisted across restarts)

## Roadmap

- **Agent planner**: Intent classification → plan → execute → synthesize
- **Grounding verifier**: Citation validation and hallucination detection
- **Trace persistence**: Database-backed trace storage for production
- **Evaluation benchmarks**: Gold Q/A datasets, retrieval MRR, routing accuracy
- **MCP integration**: Out-of-process tool boundaries (later, not first)
